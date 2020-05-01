import json

import swapper
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from netdiff.exceptions import NetdiffException
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils import get_object_or_404
from .parsers import TextParser
from .serializers import NetworkGraphSerializer

Snapshot = swapper.load_model('topology', 'Snapshot')
Topology = swapper.load_model('topology', 'Topology')


class NetworkCollectionView(generics.ListAPIView):
    """
    Data of all the topologies returned
    in NetJSON NetworkCollection format
    """

    serializer_class = NetworkGraphSerializer
    queryset = Topology.objects.filter(published=True)


class NetworkGraphView(generics.RetrieveAPIView):
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
        return Response({'detail': _('data received successfully')})


class NetworkGraphHistoryView(APIView):
    """
    History of a specific topology returned
    in NetJSON NetworkGraph format
    """

    topology_model = Topology
    snapshot_model = Snapshot

    def get(self, request, pk, format=None):
        topology = get_object_or_404(self.topology_model, pk)
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
