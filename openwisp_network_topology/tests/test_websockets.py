import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.utils.module_loading import import_string
from swapper import load_model

from .utils import CreateGraphObjectsMixin, CreateOrgMixin

Topology = load_model('topology', 'Topology')
Node = load_model('topology', 'Node')
Link = load_model('topology', 'Link')


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestTopologySockets(CreateGraphObjectsMixin, CreateOrgMixin):
    application = import_string(getattr(settings, 'ASGI_APPLICATION'))
    topology_model = Topology
    node_model = Node
    link_model = Link

    async def _get_communicator(self, admin_client, topology_id):
        session_id = admin_client.cookies['sessionid'].value
        communicator = WebsocketCommunicator(
            self.application,
            f'admin/topology/topology/{topology_id}/change/',
            headers=[
                (
                    b'cookie',
                    f'sessionid={session_id}'.encode('ascii'),
                )
            ],
        )
        return communicator

    async def test_consumer_connection(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        t = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, t.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_unauthenticated_users(self, client):
        client.cookies['sessionid'] = 'random'
        org = await database_sync_to_async(self._create_org)()
        t = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(client, t.pk)
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
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        node.label = 'test'
        await database_sync_to_async(node.full_clean)()
        await database_sync_to_async(node.save)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        await database_sync_to_async(node.delete)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        await communicator.disconnect()

    async def test_link_topology_update(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        topo = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, topo.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        node1 = await database_sync_to_async(self._create_node)(
            topology=topo, label='node-0', organization=org
        )
        response = await communicator.receive_json_from()
        node2 = await database_sync_to_async(self._create_node)(
            topology=topo, label='node-1', organization=org
        )
        response = await communicator.receive_json_from()
        link = await database_sync_to_async(self._create_link)(
            topology=topo, source=node1, target=node2, organization=org
        )
        response = await communicator.receive_json_from()
        expected_response = await database_sync_to_async(topo.json)()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        link.status = 'down'
        await database_sync_to_async(link.full_clean)()
        await database_sync_to_async(link.save)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        await database_sync_to_async(link.delete)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        await communicator.disconnect()

    async def test_topology_properties_update(self, admin_user, admin_client):
        org = await database_sync_to_async(self._create_org)()
        topo = await database_sync_to_async(self._create_topology)(organization=org)
        communicator = await self._get_communicator(admin_client, topo.pk)
        connected, _ = await communicator.connect()
        assert connected is True
        topo.name = 'test'
        await database_sync_to_async(topo.full_clean)()
        await database_sync_to_async(topo.save)()
        expected_response = await database_sync_to_async(topo.json)()
        response = await communicator.receive_json_from()
        assert response['topology'] is not None
        assert response['topology'] == expected_response
        await communicator.disconnect()
