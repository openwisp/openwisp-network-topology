import json
from copy import copy

import pytest
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.testing import ChannelsLiveServerTestCase, WebsocketCommunicator
from django.conf import settings
from django.test import tag
from django.urls import reverse
from django.utils.module_loading import import_string
from selenium.webdriver.common.by import By
from swapper import load_model

from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import SeleniumTestMixin

from .utils import CreateGraphObjectsMixin, LoadMixin

Link = load_model("topology", "Link")
Node = load_model("topology", "Node")
Topology = load_model("topology", "Topology")


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@tag("selenium_tests")
class TestRealTime(
    TestOrganizationMixin,
    CreateGraphObjectsMixin,
    LoadMixin,
    SeleniumTestMixin,
    ChannelsLiveServerTestCase,
):
    app_label = "topology"
    node_model = Node
    link_model = Link
    topology_model = Topology
    application = import_string(getattr(settings, "ASGI_APPLICATION"))

    @property
    def prefix(self):
        return f"admin:{self.app_label}"

    def setUp(self):
        org = self._create_org()
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )
        self.admin_client = self.client
        self.admin_client.force_login(self.admin)

        self.topology = self._create_topology(organization=org)
        self.node1 = self._create_node(
            label="node1",
            addresses=["192.168.0.1"],
            topology=self.topology,
            organization=org,
        )
        self.node2 = self._create_node(
            label="node2",
            addresses=["192.168.0.2"],
            topology=self.topology,
            organization=org,
        )
        self.link = self._create_link(
            source=self.node1,
            target=self.node2,
            topology=self.topology,
            status="up",
        )

    async def _get_communicator(self, admin_client, topology_id):
        session_id = admin_client.cookies["sessionid"].value
        communicator = WebsocketCommunicator(
            self.application,
            path=f"ws/network-topology/topology/{topology_id}/",
            headers=[
                (
                    b"cookie",
                    f"sessionid={session_id}".encode("ascii"),
                )
            ],
        )
        return communicator

    def update_topology_new_tab(self):
        current_url = self.web_driver.current_url
        self.web_driver.execute_script("window.open('');")
        self.web_driver.switch_to.window(self.web_driver.window_handles[-1])
        self.web_driver.get(current_url)
        self.web_driver.find_element("name", "_continue").click()
        self.web_driver.switch_to.window(self.web_driver.window_handles[0])

    async def test_real_time_link_status_update(self):
        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True

        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        await database_sync_to_async(self.link.save)()

        message = await communicator.receive_json_from()
        assert (
            json.loads(message["topology"])["links"][0]["properties"]["status"] == "up"
        )
        self.assertEqual(
            self.web_driver.execute_script("return graph.data;")["links"][0][
                "properties"
            ]["status"],
            "up",
        )

        self.link.status = "down"
        await sync_to_async(self.link.save)()

        self.update_topology_new_tab()

        message = await communicator.receive_json_from()
        assert (
            json.loads(message["topology"])["links"][0]["properties"]["status"]
            == "down"
        )

        self.assertEqual(
            self.web_driver.execute_script("return graph.data;")["links"][0][
                "properties"
            ]["status"],
            "down",
        )
        await communicator.disconnect()

    async def test_node_status_update(self):
        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True

        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()

        new_node = copy(self.node1)
        new_node.pk = None
        await database_sync_to_async(new_node.save)()
        self.update_topology_new_tab()

        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["nodes"]), 3)
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["nodes"]),
            3,
        )

        await database_sync_to_async(new_node.delete)()
        self.update_topology_new_tab()

        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["nodes"]), 2)
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["nodes"]),
            2,
        )

    async def test_node_link_update(self):
        new_link = copy(self.link)
        new_link.pk = None

        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True

        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()

        await database_sync_to_async(self.link.delete)()
        self.update_topology_new_tab()

        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["links"]), 0)
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["links"]),
            0,
        )

        await database_sync_to_async(new_link.save)()
        self.update_topology_new_tab()

        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["links"]), 1)
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["links"]),
            1,
        )
