from django.urls import reverse

from ..settings import TOPOLOGY_API_BASEURL, TOPOLOGY_API_URLCONF


class GraphVisualizerUrls:
    def get_graph_urls(self, request, pk):
        graph_path = reverse('network_graph', urlconf=TOPOLOGY_API_URLCONF, args=[pk])
        history_path = reverse(
            'network_graph_history', urlconf=TOPOLOGY_API_URLCONF, args=[pk]
        )
        if TOPOLOGY_API_BASEURL:
            graph_url = '{}{}'.format(TOPOLOGY_API_BASEURL, graph_path)
            history_url = '{}{}'.format(TOPOLOGY_API_BASEURL, history_path)
        else:
            graph_url = '{0}://{1}{2}'.format(
                request.scheme, request.get_host(), graph_path
            )
            history_url = '{0}://{1}{2}'.format(
                request.scheme, request.get_host(), history_path
            )
        return graph_url, history_url
