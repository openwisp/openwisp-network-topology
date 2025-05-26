from openwisp_network_topology.apps import OpenwispNetworkTopologyConfig


class SampleNetworkTopologyConfig(OpenwispNetworkTopologyConfig):
    name = "openwisp2.sample_network_topology"
    label = "sample_network_topology"


del OpenwispNetworkTopologyConfig
