from swapper import swappable_setting

from .base.models import AbstractDeviceNode, AbstractWifiMesh


class DeviceNode(AbstractDeviceNode):
    class Meta(AbstractDeviceNode.Meta):
        abstract = False
        swappable = swappable_setting("topology_device", "DeviceNode")


class WifiMesh(AbstractWifiMesh):
    class Meta(AbstractWifiMesh.Meta):
        abstract = False
        swappable = swappable_setting("topology_device", "WifiMesh")
