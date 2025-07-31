import json
from copy import copy
from time import sleep

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
@tag("no_parallel")
class TestRealTime(
    TestOrganizationMixin,
    CreateGraphObjectsMixin,
    LoadMixin,
    SeleniumTestMixin,
    ChannelsLiveServerTestCase,
):
    app_label = "topology"
    prefix = f"admin:{app_label}"
    node_model = Node
    link_model = Link
    topology_model = Topology
    application = import_string(getattr(settings, "ASGI_APPLICATION"))

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

    def _snooze(self):
        """Allows a bit of time for the UI to update, reduces flakyness"""
        sleep(0.2)

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

    async def test_real_time_link_status_update(self):
        # preparation
        self.link.status = "down"
        await database_sync_to_async(self.link.save)()
        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        # changing the status of a link will change it in the browser graph too
        self.link.status = "up"
        await database_sync_to_async(self.link.save)()
        message = await communicator.receive_json_from()
        assert (
            json.loads(message["topology"])["links"][0]["properties"]["status"] == "up"
        )
        self._snooze()
        self.assertEqual(
            self.web_driver.execute_script("return graph.data;")["links"][0][
                "properties"
            ]["status"],
            "up",
        )
        # test status changing to down
        self.link.status = "down"
        await sync_to_async(self.link.save)()
        message = await communicator.receive_json_from()
        assert (
            json.loads(message["topology"])["links"][0]["properties"]["status"]
            == "down"
        )
        self._snooze()
        self.assertEqual(
            self.web_driver.execute_script("return graph.data;")["links"][0][
                "properties"
            ]["status"],
            "down",
        )
        await communicator.disconnect()

    async def test_node_status_update(self):
        # preparation
        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        # saving a new node will add it to the UI
        new_node = copy(self.node1)
        new_node.pk = None
        await database_sync_to_async(new_node.save)()
        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["nodes"]), 3)
        self._snooze()
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["nodes"]),
            3,
        )
        # deleting the node from the DB will remove it from the UI
        await database_sync_to_async(new_node.delete)()
        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["nodes"]), 2)
        self._snooze()
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["nodes"]),
            2,
        )
        await communicator.disconnect()

    async def test_node_link_update(self):
        # preparation
        communicator = await self._get_communicator(self.admin_client, self.topology.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        # deleting the link from the DB will remove it from the UI
        await database_sync_to_async(self.link.delete)()
        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["links"]), 0)
        self._snooze()
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["links"]),
            0,
        )
        # adding a link will add it to the UI
        new_link = copy(self.link)
        new_link.pk = None
        await database_sync_to_async(new_link.save)()
        message = await communicator.receive_json_from()
        self.assertEqual(len(json.loads(message["topology"])["links"]), 1)
        self._snooze()
        self.assertEqual(
            len(self.web_driver.execute_script("return graph.data;")["links"]),
            1,
        )
        await communicator.disconnect()
