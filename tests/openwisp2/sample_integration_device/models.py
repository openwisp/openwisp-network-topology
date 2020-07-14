from django.db import models

from openwisp_network_topology.integrations.device.base.models import AbstractDeviceNode


class DeviceNode(AbstractDeviceNode):
    is_test = models.BooleanField(default=True)

    class Meta(AbstractDeviceNode.Meta):
        abstract = False
