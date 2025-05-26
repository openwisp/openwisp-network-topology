import swapper
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.tests.utils import TestOrganizationMixin

from .utils import CreateGraphObjectsMixin

Node = swapper.load_model("topology", "Node")
Topology = swapper.load_model("topology", "Topology")


class TestNode(CreateGraphObjectsMixin, TestOrganizationMixin, TestCase):
    topology_model = Topology
    node_model = Node
    maxDiff = 0

    def setUp(self):
        org = self._get_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label="node1", addresses=["192.168.0.1"], topology=t, organization=org
        )
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t, organization=org
        )

    def test_str(self):
        n = self.node_model(addresses=["192.168.0.1"], label="test node")
        self.assertIsInstance(str(n), str)

    def test_clean_properties(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            addresses=["192.168.0.1"], label="test node", properties=None
        )
        n.full_clean()
        self.assertEqual(n.properties, {})

    def test_node_address_single(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            addresses=["192.168.0.1"], label="test node", properties=None
        )
        n.full_clean()
        n.save()
        self.assertEqual(n.addresses[0], "192.168.0.1")
        self.assertEqual(n.addresses, ["192.168.0.1"])

    def test_node_address_multiple(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label="test node",
            addresses=["192.168.0.1", "10.0.0.1", "10.0.0.2", "10.0.0.3"],
        )
        self.assertEqual(
            n.addresses, ["192.168.0.1", "10.0.0.1", "10.0.0.2", "10.0.0.3"]
        )

    def test_node_local_addresses(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label="test node", addresses=["192.168.0.1", "10.0.0.1", "10.0.0.2"]
        )
        self.assertEqual(n.local_addresses, ["10.0.0.1", "10.0.0.2"])

    def test_node_name(self):
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=["192.168.0.1", "10.0.0.1"])
        self.assertEqual(n.name, "192.168.0.1")
        n.label = "test node"
        self.assertEqual(n.name, "test node")

    def test_node_without_name(self):
        # According to the RFC, a node MAY not have name nor local_addresses defined
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=[])
        self.assertEqual(n.name, "")

    def test_json(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label="test node",
            addresses=["192.168.0.1", "10.0.0.1"],
            properties={"gateway": True},
        )
        self.assertEqual(
            dict(n.json(dict=True)),
            {
                "id": "192.168.0.1",
                "label": "test node",
                "local_addresses": ["10.0.0.1"],
                "properties": {
                    "gateway": True,
                    "created": JSONEncoder().default(n.created),
                    "modified": JSONEncoder().default(n.modified),
                },
            },
        )
        self.assertIsInstance(n.json(), str)
        with self.subTest("testing original=True"):
            netjson = n.json(dict=True, original=True)
            self.assertNotIn("created", netjson["properties"])
            self.assertNotIn("modified", netjson["properties"])

    def test_get_from_address(self):
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=["192.168.0.1", "10.0.0.1"])
        n.full_clean()
        n.save()
        self.assertIsInstance(
            self.node_model.get_from_address("192.168.0.1", t), self.node_model
        )
        self.assertIsInstance(
            self.node_model.get_from_address("10.0.0.1", t), self.node_model
        )
        self.assertIsNone(self.node_model.get_from_address("wrong", t))

    def test_count_address(self):
        t = self.topology_model.objects.first()
        self.assertEqual(self.node_model.count_address("192.168.0.1", t), 1)
        self.assertEqual(self.node_model.count_address("0.0.0.0", t), 0)

    def test_count_address_issue_58(self):
        t = self.topology_model.objects.first()
        n1 = t._create_node(addresses=["Benz_Kalloni"])
        n1.full_clean()
        n1.save()
        n2 = t._create_node(addresses=["Kalloni"])
        n2.full_clean()
        n2.save()
        self.assertEqual(self.node_model.count_address("Benz_Kalloni", t), 1)
        self.assertEqual(self.node_model.count_address("Kalloni", t), 1)

    def test_node_auto_org(self):
        t = self.topology_model.objects.first()
        n = self.node_model(
            label="TestNode", addresses=["192.168.0.1"], properties={}, topology=t
        )
        n.full_clean()
        self.assertEqual(n.organization, t.organization)

    def test_user_properties_in_json(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            addresses=["192.168.0.1"], label="test node", properties=None
        )
        n.properties = {"gateway": True}
        n.user_properties = {"user_property": True}
        n.full_clean()
        n.save()

        with self.subTest("view json with original False"):
            data = n.json(dict=True)
            self.assertIn("gateway", data["properties"])
            self.assertIn("user_property", data["properties"])

        with self.subTest("view json with original True"):
            data = n.json(dict=True, original=True)
            self.assertIn("gateway", data["properties"])
            self.assertNotIn("user_property", data["properties"])

    def test_get_organization(self):
        org = self._get_org()
        org_topology = Topology.objects.first()
        shared_topology = self._create_topology(
            label="Shared Topology", organization=None
        )

        with self.subTest("Shared nodes can belong to shared topology"):
            try:
                shared_node = self._create_node(
                    label="shared_node",
                    addresses=["192.168.0.6"],
                    topology=shared_topology,
                    organization=None,
                )
            except ValidationError:
                self.fail("Shared topology failed to include shared node.")
            shared_node.refresh_from_db()
            self.assertEqual(shared_node.organization, None)

        with self.subTest("Non-shared nodes can belong to shared topology"):
            try:
                org_node = self._create_node(
                    label="org_node",
                    addresses=["192.168.0.7"],
                    topology=shared_topology,
                    organization=org,
                )
            except ValidationError:
                self.fail("Shared topology failed to include non-shared node.")
            org_node.refresh_from_db()
            self.assertEqual(org_node.organization, org)

        with self.subTest("Node gets organization of non-shared topology"):
            node = self._create_node(
                label="node",
                addresses=["192.168.0.8"],
                topology=org_topology,
                organization=None,
            )
            node.refresh_from_db()
            self.assertEqual(node.organization, org)

        with self.subTest(
            "ValidationError on different organization node and topology"
        ):
            with self.assertRaises(ValidationError):
                self._create_node(
                    label="node",
                    addresses=["192.168.0.9"],
                    topology=org_topology,
                    organization=self._get_org("default"),
                )
