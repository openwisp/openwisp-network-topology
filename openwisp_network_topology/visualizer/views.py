import swapper
from django.shortcuts import render
from django.views import View

from ..settings import VISUALIZER_CSS
from ..utils import get_object_or_404
from . import GraphVisualizerUrls

Topology = swapper.load_model('topology', 'Topology')


class TopologyListView(View):
    topology_model = Topology

    def get(self, request):
        topologies = self.topology_model.objects.filter(published=True)
        return render(
            request,
            'netjsongraph/list.html',
            {'topologies': topologies, 'VISUALIZER_CSS': VISUALIZER_CSS},
        )


class TopologyDetailView(View, GraphVisualizerUrls):
    topology_model = Topology

    def get(self, request, pk):
        topology = get_object_or_404(self.topology_model, pk)
        graph_url, history_url = self.get_graph_urls(request, pk)
        return render(
            request,
            'netjsongraph/detail.html',
            {
                'topology': topology,
                'graph_url': graph_url,
                'history_url': history_url,
                'VISUALIZER_CSS': VISUALIZER_CSS,
            },
        )


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
