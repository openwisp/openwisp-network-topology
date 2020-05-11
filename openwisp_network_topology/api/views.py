from django_netjsongraph.api.generics import (
    BaseNetworkCollectionView,
    BaseNetworkGraphHistoryView,
    BaseNetworkGraphView,
    BaseReceiveTopologyView,
)
from django_netjsongraph.api.serializers import NetworkGraphSerializer

from ..models import Snapshot, Topology

# TODO: use swappable model loading to define this at serializer level
NetworkGraphSerializer.Meta.model = Topology
NetworkGraphSerializer.Meta.fields = '__all__'


class NetworkCollectionView(BaseNetworkCollectionView):
    queryset = Topology.objects.filter(published=True)


class NetworkGraphView(BaseNetworkGraphView):
    queryset = Topology.objects.filter(published=True)


class ReceiveTopologyView(BaseReceiveTopologyView):
    model = Topology


class NetworkGraphHistoryView(BaseNetworkGraphHistoryView):
    topology_model = Topology
    snapshot_model = Snapshot


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
network_graph_history = NetworkGraphHistoryView.as_view()
receive_topology = ReceiveTopologyView.as_view()
