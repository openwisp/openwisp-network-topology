from django_netjsongraph.api.generics import (BaseNetworkCollectionView, BaseNetworkGraphView,
                                              BaseReceiveTopologyView)

from ..models import Topology


class NetworkCollectionView(BaseNetworkCollectionView):
    queryset = Topology.objects.filter(published=True)


class NetworkGraphView(BaseNetworkGraphView):
    queryset = Topology.objects.filter(published=True)


class ReceiveTopologyView(BaseReceiveTopologyView):
    model = Topology


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
receive_topology = ReceiveTopologyView.as_view()
