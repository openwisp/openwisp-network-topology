from django.db import models

from openwisp_network_topology.integrations.device.base.models import (
    AbstractDeviceNode,
    AbstractWifiMesh,
)


class DeviceNode(AbstractDeviceNode):
    is_test = models.BooleanField(default=True)

    class Meta(AbstractDeviceNode.Meta):
        abstract = False


class WifiMesh(AbstractWifiMesh):
    is_test = models.BooleanField(default=True)

    class Meta(AbstractWifiMesh.Meta):
        abstract = False
