from openwisp_network_topology.visualizer.views import (
    TopologyDetailView as BaseTopologyDetailView,
)
from openwisp_network_topology.visualizer.views import (
    TopologyListView as BaseTopologyListView,
)


class TopologyListView(BaseTopologyListView):
    pass


class TopologyDetailView(BaseTopologyDetailView):
    pass


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
