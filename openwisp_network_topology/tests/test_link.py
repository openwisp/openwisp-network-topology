import swapper
from django.core.exceptions import ValidationError
from django.test import TestCase

from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import catch_signal

from ..utils import link_status_changed
from .utils import CreateGraphObjectsMixin

Link = swapper.load_model("topology", "Link")
Node = swapper.load_model("topology", "Node")
Topology = swapper.load_model("topology", "Topology")


class TestLink(TestOrganizationMixin, CreateGraphObjectsMixin, TestCase):
    topology_model = Topology
    node_model = Node
    link_model = Link

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label="node1", addresses=["192.168.0.1"], topology=t, organization=org
        )
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t, organization=org
        )

    def _get_nodes(self):
        return self.node_model.objects.all()

    def test_str(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = t._create_link(source=node1, target=node2, cost=1.0)
        self.assertIsInstance(str(link), str)

    def test_clean_properties(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = t._create_link(source=node1, target=node2, cost=1.0, properties=None)
        link.full_clean()
        self.assertEqual(link.properties, {})

    def test_clean_properties_status(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = t._create_link(
            source=node1, target=node2, cost=1.0, properties={"status": "up"}
        )
        link.full_clean()
        # status must not be saved in properties or it will override the real status
        self.assertEqual(link.properties, {})

    def test_same_source_and_target_id(self):
        t = self.topology_model.objects.first()
        node_id = self.node_model.objects.first().pk
        link = t._create_link(source_id=node_id, target_id=node_id, cost=1)
        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_same_source_and_target(self):
        t = self.topology_model.objects.first()
        node = self.node_model.objects.first()
        link = t._create_link(source=node, target=node, cost=1)
        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_json(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = t._create_link(
            source=node1,
            target=node2,
            cost=1.0,
            cost_text="100mbit/s",
            properties={"pretty": True},
        )
        self.assertEqual(
            dict(link.json(dict=True)),
            {
                "source": "192.168.0.1",
                "target": "192.168.0.2",
                "cost": 1.0,
                "cost_text": "100mbit/s",
                "properties": {
                    "pretty": True,
                    "status": "up",
                    "created": link.created,
                    "modified": link.modified,
                    "status_changed": link.status_changed,
                },
            },
        )
        self.assertIsInstance(link.json(), str)
        link.status = "down"
        link.save()
        link.refresh_from_db()
        netjson = link.json(dict=True)
        with self.subTest("status should not be saved in properties"):
            self.assertNotIn("status", link.properties)
        with self.subTest("status should not be overridden"):
            self.assertEqual(netjson["properties"]["status"], "down")
        with self.subTest("testing original=True"):
            netjson = link.json(dict=True, original=True)
            self.assertNotIn("status", netjson["properties"])
            self.assertNotIn("status_changed", netjson["properties"])
            self.assertNotIn("created", netjson["properties"])
            self.assertNotIn("modified", netjson["properties"])

    def test_get_from_nodes(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = t._create_link(
            source=node1,
            target=node2,
            cost=1.0,
            cost_text="100mbit/s",
            properties='{"pretty": true}',
        )
        link.full_clean()
        link.save()
        link = self.link_model.get_from_nodes("192.168.0.1", "192.168.0.2", t)
        self.assertIsInstance(link, self.link_model)
        link = self.link_model.get_from_nodes("wrong", "wrong", t)
        self.assertIsNone(link)

    def test_status_change_signal_sent(self):
        self.signal_was_called = False
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        with catch_signal(link_status_changed) as handler:
            link = t._create_link(source=node1, target=node2, cost=1.0, status="up")
            link.save()
            handler.assert_not_called()
        with catch_signal(link_status_changed) as handler:
            link.status = "down"
            link.save()
        handler.assert_called_once_with(
            link=link, sender=self.link_model, signal=link_status_changed
        )
        self.assertEqual(link.status, "down")

    def test_validate_organization(self):
        org1 = self._get_org()
        org1_topology = self.topology_model.objects.first()
        org1_node1, org1_node2 = self._get_nodes()
        shared_topology = self._create_topology(label="shared", organization=None)
        org2 = self._create_org(name="org2")
        org2_node1 = self._create_node(
            label="org2_node1",
            addresses=["192.168.0.3"],
            topology=shared_topology,
            organization=org2,
        )

        with self.subTest("Test toplogy and nodes belongs to different organizations"):
            # Test source node
            link = self.link_model(
                source=org2_node1,
                target=org2_node1,
                cost=1.0,
                cost_text="100mbit/s",
                topology=org1_topology,
            )
            with self.assertRaises(ValidationError) as context_manager:
                link.full_clean()
            source_expected_error = (
                "Source node and topology should have same organization."
            )
            target_expected_error = (
                "Target node and topology should have same organization."
            )
            self.assertIn(
                source_expected_error, context_manager.exception.message_dict["source"]
            )
            self.assertIn(
                target_expected_error, context_manager.exception.message_dict["target"]
            )

        with self.subTest("Test link gets organization of non-shared topology"):
            link = self.link_model(
                source=org1_node1,
                target=org1_node2,
                cost=1.0,
                cost_text="100mbit/s",
                topology=org1_topology,
            )
            link.full_clean()
            self.assertEqual(link.organization, org1_topology.organization)

        with self.subTest("Test non-shared link of shared topology"):
            # Since source and target nodes belong to the same organization,
            # link will get organization of the nodes
            source_node = self._create_node(
                label="org1_node1_shared_topology",
                addresses=["10.0.0.1"],
                topology=shared_topology,
                organization=org1,
            )
            target_node = self._create_node(
                label="org1_node2_shared_topology",
                addresses=["10.0.0.2"],
                topology=shared_topology,
                organization=org1,
            )
            link = self.link_model(
                source=source_node,
                target=target_node,
                cost=1.0,
                cost_text="100mbit/s",
                topology=shared_topology,
            )
            link.full_clean()
            self.assertEqual(link.organization, org1)

        with self.subTest("Test shared link of shared topology"):
            # Since source and target nodes belongs to different organizations,
            # link will be shared.
            source_node = self._create_node(
                label="org1_node1_shared_topology",
                addresses=["10.0.0.3"],
                topology=shared_topology,
                organization=org1,
            )
            target_node = self._create_node(
                label="org2_node1_shared_topology",
                addresses=["10.0.0.4"],
                topology=shared_topology,
                organization=org2,
            )
            link = self.link_model(
                source=source_node,
                target=target_node,
                cost=1.0,
                cost_text="100mbit/s",
                topology=shared_topology,
            )
            link.full_clean()
            self.assertEqual(link.organization, None)

    def test_user_properties_in_json(self):
        t = self.topology_model.objects.first()
        node1, node2 = self._get_nodes()
        link = self.link_model(
            source=node1, target=node2, cost=1.0, cost_text="100mbit/s", topology=t
        )
        link.properties = {"wired": True}
        link.user_properties = {"user_property": True}
        link.full_clean()
        link.save()

        with self.subTest("view json when original is False"):
            data = link.json(dict=True)
            self.assertIn("wired", data["properties"])
            self.assertIn("user_property", data["properties"])

        with self.subTest("view json when original is True"):
            data = link.json(dict=True, original=True)
            self.assertIn("wired", data["properties"])
            self.assertNotIn("user_property", data["properties"])
