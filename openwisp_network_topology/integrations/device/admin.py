from django.contrib import admin
from swapper import load_model

from openwisp_network_topology.admin import TopologyAdmin

from . import settings as app_settings

WifiMesh = load_model("topology_device", "WifiMesh")
Topology = load_model("topology", "Topology")


class WifiMeshInlineAdmin(admin.StackedInline):
    model = WifiMesh
    extra = 0
    max_num = 1


if app_settings.WIFI_MESH_INTEGRATION:
    TopologyAdmin.inlines = list(TopologyAdmin.inlines) + [WifiMeshInlineAdmin]
