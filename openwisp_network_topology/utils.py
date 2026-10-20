import sys

from django.core.exceptions import ValidationError
from django.dispatch import Signal
from django.http import Http404
from django.shortcuts import get_object_or_404 as get_obj_or_404
from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

link_status_changed = Signal()
link_status_changed.__doc__ = """
Providing arguments: ['link']
"""

DISABLED_ORGANIZATION_ERROR = _(
    "This object belongs to a disabled organization and cannot be modified."
)


def is_write_blocked(obj):
    """
    Whether write operations must be skipped for ``obj``.

    Duck-typed so it works for both topology objects and devices: a
    deactivated device, or an object belonging to a disabled
    organization, blocks writes; shared objects (no organization) do not.
    """
    if obj is None:
        return False
    if hasattr(obj, "is_deactivated") and obj.is_deactivated():
        return True
    organization = getattr(obj, "organization", None)
    return organization is not None and not organization.is_active


def validate_organization_enabled(*objects):
    for obj in objects:
        if is_write_blocked(obj):
            raise ValidationError(DISABLED_ORGANIZATION_ERROR)


def print_info(message):  # pragma no cover
    """
    print info message if calling from management command ``update_all``
    """
    if "update_topology" in sys.argv:
        print("{0}\n".format(message))


def get_object_or_404(model, pk, **kwargs):
    """
    retrieves topology with specified arguments or raises 404
    """
    kwargs.update({"pk": pk, "published": True})
    try:
        return get_obj_or_404(model, **kwargs)
    except ValidationError:
        raise Http404()


def get_api_urls(views_module):
    """
    used by third party apps to reduce boilerplate
    """
    urls = [
        path(
            "network-topology/topology/",
            views_module.network_collection,
            name="network_collection",
        ),
        path(
            "network-topology/topology/<uuid:pk>/",
            views_module.network_graph,
            name="network_graph",
        ),
        path(
            "network-topology/topology/<uuid:pk>/history/",
            views_module.network_graph_history,
            name="network_graph_history",
        ),
        path(
            "network-topology/topology/<uuid:pk>/receive/",
            views_module.receive_topology,
            name="receive_topology",
        ),
        path("network-topology/node/", views_module.node_list, name="node_list"),
        path(
            "network-topology/node/<uuid:pk>/",
            views_module.node_detail,
            name="node_detail",
        ),
        path("network-topology/link/", views_module.link_list, name="link_list"),
        path(
            "network-topology/link/<uuid:pk>/",
            views_module.link_detail,
            name="link_detail",
        ),
    ]
    return urls


def get_visualizer_urls(views_module):
    """
    used by third party apps to reduce boilerplate
    """
    urls = [
        path("", views_module.topology_list, name="topology_list"),
        re_path(
            r"^topology/(?P<pk>[^/]+)/$",
            views_module.topology_detail,
            name="topology_detail",
        ),
    ]
    return urls
