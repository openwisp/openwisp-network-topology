import swapper
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from ..settings import TOPOLOGY_API_AUTH_REQUIRED, VISUALIZER_CSS
from ..utils import get_object_or_404
from . import GraphVisualizerUrls

Topology = swapper.load_model("topology", "Topology")


class TopologyListView(View):
    topology_model = Topology

    def get(self, request):
        topologies = self.topology_model.objects.filter(published=True)
        user = request.user
        if TOPOLOGY_API_AUTH_REQUIRED and not user.is_superuser:
            auth_perm = check_auth_perm(request)
            if auth_perm is not None:
                return auth_perm
            topologies = topologies.filter(organization__in=user.organizations_managed)
        return render(
            request,
            "netjsongraph/list.html",
            {"topologies": topologies, "VISUALIZER_CSS": VISUALIZER_CSS},
        )


class TopologyDetailView(View, GraphVisualizerUrls):
    topology_model = Topology

    def get(self, request, pk):
        topology = get_object_or_404(self.topology_model, pk)
        user = request.user
        if TOPOLOGY_API_AUTH_REQUIRED and not user.is_superuser:
            auth_perm = check_auth_perm(request)
            if auth_perm is not None:
                return auth_perm
            if not user.is_manager(topology.organization):
                detail = _(
                    "User is not a manager of the organization to "
                    "which the requested resource belongs."
                )
                return HttpResponseForbidden(detail)
        graph_url, history_url = self.get_graph_urls(request, pk)
        return render(
            request,
            "netjsongraph/detail.html",
            {
                "topology": topology,
                "graph_url": graph_url,
                "history_url": history_url,
                "VISUALIZER_CSS": VISUALIZER_CSS,
            },
        )


def check_auth_perm(request):
    user = request.user
    app_label = Topology._meta.app_label.lower()
    model = Topology._meta.object_name.lower()
    change_perm = f"{app_label}.change_{model}"
    view_perm = f"{app_label}.view_{model}"
    if not user.is_authenticated:
        return HttpResponseForbidden(_("Authentication credentials were not provided."))
    if not (user.has_perm(change_perm) or user.has_perm(view_perm)):
        return HttpResponseForbidden(
            _("You do not have permission to perform this action.")
        )


topology_list = TopologyListView.as_view()
topology_detail = TopologyDetailView.as_view()
