import swapper
from openwisp_ipam.tests import CreateModelsMixin as SubnetIpamMixin

from openwisp_controller.config.tests.utils import (
    CreateConfigTemplateMixin,
    TestVpnX509Mixin,
    TestWireguardVpnMixin,
)
from openwisp_network_topology.tests.utils import CreateGraphObjectsMixin
from openwisp_users.tests.utils import TestOrganizationMixin

Node = swapper.load_model("topology", "Node")

Topology = swapper.load_model("topology", "Topology")


class TopologyTestMixin(
    TestVpnX509Mixin,
    TestWireguardVpnMixin,
    SubnetIpamMixin,
    CreateConfigTemplateMixin,
    CreateGraphObjectsMixin,
    TestOrganizationMixin,
):
    topology_model = Topology
    node_model = Node

    def _init_test_node(
        self,
        topology,
        addresses=None,
        label="test",
        common_name=None,
        create=True,
    ):
        if not addresses:
            addresses = ["netjson_id"]
        node = Node(
            organization=topology.organization,
            topology=topology,
            label=label,
            addresses=addresses,
            properties={"common_name": common_name},
        )
        if create:
            node.full_clean()
            node.save()
        return node

    def _init_wireguard_test_node(self, topology, addresses=[], create=True, **kwargs):
        if not addresses:
            addresses = ["public_key"]
        properties = {
            "preshared_key": None,
            "endpoint": None,
            "latest_handsake": "0",
            "transfer_rx": "0",
            "transfer_tx": "0",
            "persistent_keepalive": "off",
            "allowed_ips": ["10.0.0.2/32"],
        }
        properties.update(kwargs)
        allowed_ips = properties.get("allowed_ips")
        node = Node(
            organization=topology.organization,
            topology=topology,
            label=",".join(allowed_ips),
            addresses=addresses,
            properties=properties,
        )
        if create:
            node.full_clean()
            node.save()
        return node

    def _create_wireguard_test_env(self, parser):
        org = self._get_org()
        device, _, _ = self._create_wireguard_vpn_template()
        device.organization = org
        topology = self._create_topology(organization=org, parser=parser)
        return topology, device

    def _create_test_env(self, parser):
        organization = self._get_org()
        vpn = self._create_vpn(name="test VPN", organization=organization)
        self._create_template(
            name="VPN",
            type="vpn",
            vpn=vpn,
            config=vpn.auto_client(),
            default=True,
            organization=organization,
        )
        vpn2 = self._create_vpn(name="test VPN2", ca=vpn.ca, organization=organization)
        self._create_template(
            name="VPN2",
            type="vpn",
            vpn=vpn2,
            config=vpn.auto_client(),
            default=True,
            organization=organization,
        )
        device = self._create_device(organization=organization)
        config = self._create_config(device=device)
        topology = self._create_topology(organization=organization, parser=parser)
        cert = config.vpnclient_set.first().cert
        return topology, device, cert
