import swapper

from openwisp_network_topology.integrations.device.tests import (
    TestControllerIntegration as BaseTestControllerIntegration,
)
from openwisp_network_topology.integrations.device.tests import (
    TestMonitoringIntegration as BaseTestMonitoringIntegration,
)

DeviceNode = swapper.load_model('topology_device', 'DeviceNode')


class TestControllerIntegration(BaseTestControllerIntegration):
    def test_device_node_custom(self):
        self.assertTrue(DeviceNode().is_test)


class TestMonitoringIntegration(BaseTestMonitoringIntegration):
    pass


del BaseTestControllerIntegration
del BaseTestMonitoringIntegration
