from unittest.mock import patch
from uuid import uuid4

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils.module_loading import import_string
from swapper import load_model

from openwisp_users.tests.utils import TestOrganizationMixin

from .. import settings as app_settings
from .utils import CreateGraphObjectsMixin

Topology = load_model("topology", "Topology")
Node = load_model("topology", "Node")
Link = load_model("topology", "Link")


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestTopologySockets(CreateGraphObjectsMixin, TestOrganizationMixin):
    node_model = Node
    link_model = Link
    topology_model = Topology
    application = import_string(getattr(settings, "ASGI_APPLICATION"))

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

    async def _assert_connection_superuser(self, admin_client, conn=True):
        org = await database_sync_to_async(self._create_org)()
        t = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, t.pk)
        connected, _ = await communicator.connect()
        assert connected is conn
        await communicator.disconnect()

    async def _assert_connection_org_manager(self, client, view_perm=True, conn=True):
        org = await database_sync_to_async(self._create_org)()
        test_user = await database_sync_to_async(self._create_user)(
            username="test-user-org-manager", email="test@orgmanger.com", is_staff=True
        )
        await database_sync_to_async(self._create_org_user)(
            is_admin=True, user=test_user, organization=org
        )
        t = await database_sync_to_async(self._create_topology)(organization=org)
        if view_perm:
            topology_view_permission = await Permission.objects.aget(
                codename="view_topology"
            )
            await test_user.user_permissions.aadd(topology_view_permission)
        await database_sync_to_async(client.force_login)(test_user)
        communicator = await self._get_communicator(client, t.pk)
        connected, _ = await communicator.connect()
        assert connected is conn
        await communicator.disconnect()

    async def _assert_connection_unauth_user(self, client, conn=True):
        client.cookies["sessionid"] = "unauthenticated_user"
        org = await database_sync_to_async(self._create_org)()
        t = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(client, t.pk)
        connected, _ = await communicator.connect()
        assert connected is conn
        await communicator.disconnect()

    async def test_consumer_connection_superuser(self, admin_client):
        await self._assert_connection_superuser(admin_client)

    async def test_consumer_connection_org_manager_view_perm(self, client):
        await self._assert_connection_org_manager(client)

    async def test_consumer_connection_org_manager_without_view_perm(self, client):
        await self._assert_connection_org_manager(client, view_perm=False, conn=False)

    async def test_consumer_connection_unauth_user(self, client):
        await self._assert_connection_unauth_user(client, conn=False)

    @patch.object(app_settings, "TOPOLOGY_API_AUTH_REQUIRED", False)
    async def test_consumer_connection_auth_disabled_superuser(self, admin_client):
        await self._assert_connection_superuser(admin_client)

    @patch.object(app_settings, "TOPOLOGY_API_AUTH_REQUIRED", False)
    async def test_consumer_connection_auth_disabled_org_manager(self, client):
        await self._assert_connection_org_manager(client)

    @patch.object(app_settings, "TOPOLOGY_API_AUTH_REQUIRED", False)
    async def test_consumer_connection_auth_disabled_unauth_user(self, client):
        await self._assert_connection_unauth_user(client)

    async def test_consumer_connection_unexisting_topology(
        self, admin_user, admin_client
    ):
        org = await database_sync_to_async(self._create_org)()
        await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, uuid4())
        connected, _ = await communicator.connect()
        assert connected is False
        await communicator.disconnect()

    async def test_node_topology_update(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        topo = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, topo.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        node = await database_sync_to_async(self._create_node)(
            topology=topo, organization=org
        )
        response = await communicator.receive_json_from()
        expected_response = await database_sync_to_async(topo.json)()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        node.label = "test"
        await database_sync_to_async(node.full_clean)()
        await database_sync_to_async(node.save)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        await node.adelete()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        await communicator.disconnect()

    async def test_link_topology_update(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        topo = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, topo.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        node1 = await database_sync_to_async(self._create_node)(
            topology=topo, label="node-0", organization=org
        )
        response = await communicator.receive_json_from()
        node2 = await database_sync_to_async(self._create_node)(
            topology=topo, label="node-1", organization=org
        )
        response = await communicator.receive_json_from()
        link = await database_sync_to_async(self._create_link)(
            topology=topo, source=node1, target=node2, organization=org
        )
        response = await communicator.receive_json_from()
        expected_response = await database_sync_to_async(topo.json)()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        link.status = "down"
        await database_sync_to_async(link.full_clean)()
        await link.asave()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        await link.adelete()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        await communicator.disconnect()

    async def test_topology_properties_update(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        topo = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, topo.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        topo.name = "test"
        await database_sync_to_async(topo.full_clean)()
        await topo.asave()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response["topology"] is not None
        assert response["topology"] == expected_response
        await communicator.disconnect()
