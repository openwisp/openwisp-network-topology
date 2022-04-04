from openwisp_network_topology.api.views import LinkDetailView as BaseLinkDetailView
from openwisp_network_topology.api.views import (
    LinkListCreateView as BaseLinkListCreateView,
)
from openwisp_network_topology.api.views import (
    NetworkCollectionView as BaseNetworkCollectionView,
)
from openwisp_network_topology.api.views import (
    NetworkGraphHistoryView as BaseNetworkGraphHistoryView,
)
from openwisp_network_topology.api.views import NetworkGraphView as BaseNetworkGraphView
from openwisp_network_topology.api.views import NodeDetailView as BaseNodeDetailView
from openwisp_network_topology.api.views import (
    NodeListCreateView as BaseNodeListCreateView,
)
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


class NodeListCreateView(BaseNodeListCreateView):
    pass


class NodeDetailView(BaseNodeDetailView):
    pass


class LinkListCreateView(BaseLinkListCreateView):
    pass


class LinkDetailView(BaseLinkDetailView):
    pass


network_collection = NetworkCollectionView.as_view()
network_graph = NetworkGraphView.as_view()
network_graph_history = NetworkGraphHistoryView.as_view()
receive_topology = ReceiveTopologyView.as_view()
node_list = NodeListCreateView.as_view()
node_detail = NodeDetailView.as_view()
link_list = LinkListCreateView.as_view()
link_detail = LinkDetailView.as_view()
