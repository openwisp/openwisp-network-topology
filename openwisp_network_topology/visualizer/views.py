from django_netjsongraph.visualizer.generics import BaseTopologyDetailView, BaseTopologyListView

from ..models import Topology


class TopologyListView(BaseTopologyListView):
    topology_model = Topology


class TopologyDetailView(BaseTopologyDetailView):
    topology_model = Topology


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
