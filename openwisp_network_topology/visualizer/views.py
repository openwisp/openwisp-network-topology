from ..models import Topology
from .generics import BaseTopologyDetailView, BaseTopologyListView


class TopologyListView(BaseTopologyListView):
    topology_model = Topology


class TopologyDetailView(BaseTopologyDetailView):
    topology_model = Topology


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
