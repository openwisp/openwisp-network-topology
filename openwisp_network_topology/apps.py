from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from swapper import get_model_name

from openwisp_utils.admin_theme.menu import register_menu_group

from .settings import SIGNALS


class OpenwispNetworkTopologyConfig(AppConfig):
    name = "openwisp_network_topology"
    label = "topology"
    verbose_name = _("Network Topology")

    def ready(self, *args, **kwargs):
        if SIGNALS:  # pragma: nocover
            __import__(SIGNALS)
        from .signals import broadcast_topology, update_topology

        update_topology.connect(broadcast_topology)
        self.register_menu_groups()

    def register_menu_groups(self):
        register_menu_group(
            position=110,
            config={
                "label": "Network Topology",
                "items": {
                    1: {
                        "label": _("Topologies"),
                        "model": get_model_name("topology", "Topology"),
                        "name": "changelist",
                        "icon": "ow-topology",
                    },
                    2: {
                        "label": _("Nodes"),
                        "model": get_model_name("topology", "Node"),
                        "name": "changelist",
                        "icon": "ow-node",
                    },
                    3: {
                        "label": _("Links"),
                        "model": get_model_name("topology", "Link"),
                        "name": "changelist",
                        "icon": "ow-link",
                    },
                },
                "icon": "ow-network-topology",
            },
        )
