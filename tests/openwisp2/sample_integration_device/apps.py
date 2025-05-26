from openwisp_network_topology.integrations.device.apps import (
    OpenwispTopologyDeviceConfig as BaseAppConfig,
)


class OpenwispTopologyDeviceConfig(BaseAppConfig):
    name = "openwisp2.sample_integration_device"
    label = "sample_integration_device"


del BaseAppConfig
