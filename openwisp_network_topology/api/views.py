import json
import logging

import swapper
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from netdiff.exceptions import NetdiffException
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import (
    BasePermission,
    DjangoModelPermissions,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from openwisp_users.api.authentication import BearerAuthentication
from openwisp_users.api.permissions import IsOrganizationManager

from .. import settings as app_settings
from ..utils import get_object_or_404
from .parsers import TextParser
from .serializers import NetworkGraphSerializer

logger = logging.getLogger(__name__)
Snapshot = swapper.load_model('topology', 'Snapshot')
Topology = swapper.load_model('topology', 'Topology')


class HasGetMethodPermission(BasePermission):
    def has_permission(self, request, view):
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request)

    def check_permission(self, request):
        user = request.user
        app_label = Topology._meta.app_label.lower()
        model = Topology._meta.object_name.lower()
        change_perm = f'{app_label}.change_{model}'
        view_perm = f'{app_label}.view_{model}'
        if user.is_authenticated:
            if user.is_superuser or request.method != 'GET':
                return True
            if request.method == 'GET' and (
                user.has_permission(change_perm) or user.has_permission(view_perm)
            ):
                return True
        return False


class RequireAuthentication(APIView):

    if app_settings.TOPOLOGY_API_AUTH_REQUIRED:
        authentication_classes = [
            SessionAuthentication,
            BasicAuthentication,
            BearerAuthentication,
        ]
        permission_classes = [
            IsAuthenticated,
            IsOrganizationManager,
            DjangoModelPermissions,
            HasGetMethodPermission,
        ]


class NetworkCollectionView(generics.ListAPIView, RequireAuthentication):
    """
    Data of all the topologies returned
    in NetJSON NetworkCollection format
    """

    serializer_class = NetworkGraphSerializer
    queryset = Topology.objects.filter(published=True)

    def list(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if user.is_authenticated:
            queryset = queryset.filter(organization__in=user.organizations_managed)
        return queryset


class NetworkGraphView(generics.RetrieveAPIView, RequireAuthentication):
    """
    Data of a specific topology returned
    in NetJSON NetworkGraph format
    """

    serializer_class = NetworkGraphSerializer
    queryset = Topology.objects.filter(published=True)


class ReceiveTopologyView(APIView):
    """
    This views allow nodes to send topology data using the RECEIVE strategy.

    Required query string parameters:
        * key

    Allowed content-types:
        * text/plain
    """

    model = Topology
    parser_classes = (TextParser,)

    def post(self, request, pk, format=None):
        topology = get_object_or_404(self.model, pk, strategy='receive')
        key = request.query_params.get('key')
        # wrong content type: 415
        if request.content_type != 'text/plain':
            return Response(
                {'detail': _('expected content type "text/plain"')}, status=415
            )
        # missing key: 400
        if not key:
            return Response(
                {'detail': _('missing required "key" parameter')}, status=400
            )
        # wrong key 403
        if topology.key != key:
            return Response({'detail': _('wrong key')}, status=403)
        try:
            topology.receive(request.data)
        except NetdiffException as e:
            error = _(
                'Supplied data not recognized as %s, '
                'got exception of type "%s" '
                'with message "%s"'
            ) % (topology.get_parser_display(), e.__class__.__name__, e)
            return Response({'detail': error}, status=400)
        success_message = _('data received successfully')
        deprecated_url = reverse('receive_topology_deprecated', args=[pk])
        if request.path == deprecated_url:
            expected_path = reverse('receive_topology', args=[pk])
            expected_path = f'{expected_path}?key={key}'
            warning = _(
                'This URL is depercated and will be removed in '
                f'future versions, use {expected_path}'
            )
            logger.warning(warning)
            success_message = f'{success_message}. {warning}'
        return Response({'detail': success_message})


class NetworkGraphHistoryView(RequireAuthentication):
    """
    History of a specific topology returned
    in NetJSON NetworkGraph format
    """

    topology_model = Topology
    snapshot_model = Snapshot
    queryset = topology_model.objects.all()  # Required for DjangoModelPermissions

    def get(self, request, pk, format=None):
        topology = get_object_or_404(self.topology_model, pk)
        self.check_object_permissions(request, topology)
        date = request.query_params.get('date')
        options = dict(topology=topology, date=date)
        # missing date: 400
        if not date:
            return Response(
                {'detail': _('missing required "date" parameter')}, status=400
            )
        try:
            s = self.snapshot_model.objects.get(**options)
            return Response(json.loads(s.data))
        except self.snapshot_model.DoesNotExist:
            return Response(
                {'detail': _('no snapshot found for this date')}, status=404
            )
        except ValidationError:
            return Response({'detail': _('invalid date supplied')}, status=403)


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
network_graph_history = NetworkGraphHistoryView.as_view()
receive_topology = ReceiveTopologyView.as_view()
