import swapper
from django.core.management.base import BaseCommand
from django.db.models import Q


class BaseCreateDeviceNodeCommand(BaseCommand):
    help = "Create initial DeviceNode objects"

    def handle(self, *args, **kwargs):
        Node = swapper.load_model("topology", "Node")
        DeviceNode = swapper.load_model("topology_device", "DeviceNode")
        queryset = Node.objects.select_related("topology").filter(
            Q(topology__parser="netdiff.OpenvpnParser")
            | Q(topology__parser="netdiff.WireguardParser")
            | Q(topology__parser="netdiff.ZeroTierParser")
        )
        for node in queryset.iterator():
            DeviceNode.auto_create(node)
