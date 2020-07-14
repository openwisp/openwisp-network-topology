from swapper import swappable_setting

from .base.models import AbstractDeviceNode


class DeviceNode(AbstractDeviceNode):
    class Meta(AbstractDeviceNode.Meta):
        abstract = False
        swappable = swappable_setting('topology_device', 'DeviceNode')
