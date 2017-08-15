from django_netjsongraph.api.generics import (BaseNetworkCollectionView, BaseNetworkGraphHistoryView,
                                              BaseNetworkGraphView, BaseReceiveTopologyView)

from ..models import Snapshot, Topology


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
