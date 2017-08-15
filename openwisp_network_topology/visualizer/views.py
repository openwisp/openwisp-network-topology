from django_netjsongraph.visualizer.generics import (BaseTopologyDetailView, BaseTopologyHistoryView,
                                                     BaseTopologyListView)

from ..models import Topology


class TopologyListView(BaseTopologyListView):
    topology_model = Topology


class TopologyDetailView(BaseTopologyDetailView):
    topology_model = Topology


class TopologyHistoryView(BaseTopologyHistoryView):
    topology_model = Topology


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
topology_history = TopologyHistoryView.as_view()
