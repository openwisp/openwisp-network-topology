from openwisp_network_topology.api.views import (
    NetworkCollectionView as BaseNetworkCollectionView,
)
from openwisp_network_topology.api.views import (
    NetworkGraphHistoryView as BaseNetworkGraphHistoryView,
)
from openwisp_network_topology.api.views import NetworkGraphView as BaseNetworkGraphView
from openwisp_network_topology.api.views import (
    ReceiveTopologyView as BaseReceiveTopologyView,
)


class NetworkCollectionView(BaseNetworkCollectionView):
    pass


class NetworkGraphView(BaseNetworkGraphView):
    pass


class ReceiveTopologyView(BaseReceiveTopologyView):
    pass


class NetworkGraphHistoryView(BaseNetworkGraphHistoryView):
    pass


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
network_graph_history = NetworkGraphHistoryView.as_view()
receive_topology = ReceiveTopologyView.as_view()
