import json
import logging

import swapper
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from netdiff.exceptions import NetdiffException
from rest_framework import generics, pagination
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from openwisp_users.api.authentication import BearerAuthentication
from openwisp_users.api.mixins import FilterByOrganizationManaged, ProtectedAPIMixin
from openwisp_users.api.permissions import DjangoModelPermissions, IsOrganizationManager

from .. import settings as app_settings
from ..utils import get_object_or_404
from .filters import LinkFilter, NetworkCollectionFilter, NodeFilter
from .parsers import TextParser
from .serializers import (
    LinkSerializer,
    NetworkGraphSerializer,
    NetworkGraphUpdateSerializer,
    NodeSerializer,
)

logger = logging.getLogger(__name__)
Snapshot = swapper.load_model("topology", "Snapshot")
Topology = swapper.load_model("topology", "Topology")
Node = swapper.load_model("topology", "Node")
Link = swapper.load_model("topology", "Link")


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
        ]


class ListViewPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UnpublishedTopologyFilterMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("include_unpublished"):
            return qs
        return qs.filter(published=True)


class NetworkCollectionView(
    UnpublishedTopologyFilterMixin,
    RequireAuthentication,
    FilterByOrganizationManaged,
    generics.ListCreateAPIView,
):
    """
    Data of all the topologies returned
    in NetJSON NetworkCollection format.
    """

    serializer_class = NetworkGraphSerializer
    queryset = Topology.objects.select_related("organization")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NetworkCollectionFilter

    def list(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)

    def get_success_headers(self, data):
        """
        Remove `LOCATION` option from the
        header when URL field is present.
        """
        return {}


class NetworkGraphView(
    UnpublishedTopologyFilterMixin,
    RequireAuthentication,
    FilterByOrganizationManaged,
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Data of a specific topology returned
    in NetJSON NetworkGraph format.
    """

    serializer_class = NetworkGraphUpdateSerializer
    queryset = Topology.objects.select_related("organization")


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

    def _validate_request(self, request, topology):
        key = request.query_params.get("key")
        # wrong content type: 415
        if request.content_type != "text/plain":
            return Response(
                {"detail": _('expected content type "text/plain"')}, status=415
            )
        # missing key: 400
        if not key:
            return Response(
                {"detail": _('missing required "key" parameter')}, status=400
            )
        # wrong key 403
        if topology.key != key:
            return Response({"detail": _("wrong key")}, status=403)
        return

    def post(self, request, pk, format=None):
        topology = get_object_or_404(self.model, pk, strategy="receive")
        validation_response = self._validate_request(request, topology)
        if validation_response:
            return validation_response
        try:
            topology.receive(request.data)
        except NetdiffException as e:
            error = _(
                "Supplied data not recognized as %s, "
                'got exception of type "%s" '
                'with message "%s"'
            ) % (topology.get_parser_display(), e.__class__.__name__, e)
            return Response({"detail": error}, status=400)
        success_message = _("data received successfully")
        return Response({"detail": success_message})


class NetworkGraphHistoryView(RequireAuthentication):
    """
    History of a specific topology returned
    in NetJSON NetworkGraph format.
    """

    topology_model = Topology
    snapshot_model = Snapshot
    queryset = topology_model.objects.all()  # Required for DjangoModelPermissions

    def get(self, request, pk, format=None):
        topology = get_object_or_404(self.topology_model, pk)
        self.check_object_permissions(request, topology)
        date = request.query_params.get("date")
        options = dict(topology=topology, date=date)
        # missing date: 400
        if not date:
            return Response(
                {"detail": _('missing required "date" parameter')}, status=400
            )
        try:
            s = self.snapshot_model.objects.get(**options)
            return Response(json.loads(s.data))
        except self.snapshot_model.DoesNotExist:
            return Response(
                {"detail": _("no snapshot found for this date")}, status=404
            )
        except ValidationError:
            return Response({"detail": _("invalid date supplied")}, status=403)


class NodeListCreateView(
    ProtectedAPIMixin, FilterByOrganizationManaged, generics.ListCreateAPIView
):
    queryset = Node.objects.order_by("-created")
    serializer_class = NodeSerializer
    pagination_class = ListViewPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NodeFilter


class NodeDetailView(
    ProtectedAPIMixin,
    FilterByOrganizationManaged,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Node.objects.all().select_related("topology")
    serializer_class = NodeSerializer


class LinkListCreateView(
    ProtectedAPIMixin, FilterByOrganizationManaged, generics.ListCreateAPIView
):
    queryset = Link.objects.select_related(
        "topology",
        "source",
        "target",
    ).order_by("-created")
    serializer_class = LinkSerializer
    pagination_class = ListViewPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LinkFilter


class LinkDetailView(
    ProtectedAPIMixin,
    FilterByOrganizationManaged,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Link.objects.select_related(
        "topology",
        "source",
        "target",
    )
    serializer_class = LinkSerializer


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
network_graph_history = NetworkGraphHistoryView.as_view()
receive_topology = ReceiveTopologyView.as_view()
node_list = NodeListCreateView.as_view()
node_detail = NodeDetailView.as_view()
link_list = LinkListCreateView.as_view()
link_detail = LinkDetailView.as_view()
