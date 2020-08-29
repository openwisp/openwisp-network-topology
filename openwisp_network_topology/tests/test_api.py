from unittest.mock import patch

import swapper
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.views import APIView

from openwisp_users.tests.utils import TestOrganizationMixin

from .utils import CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin, UnpublishMixin

Link = swapper.load_model('topology', 'Link')
Node = swapper.load_model('topology', 'Node')
Snapshot = swapper.load_model('topology', 'Snapshot')
Topology = swapper.load_model('topology', 'Topology')
OrganizationUser = swapper.load_model('openwisp_users', 'OrganizationUser')


class TestApi(
    CreateGraphObjectsMixin,
    CreateOrgMixin,
    UnpublishMixin,
    LoadMixin,
    TestOrganizationMixin,
    TestCase,
):
    list_url = reverse('network_collection')
    topology_model = Topology
    node_model = Node
    link_model = Link
    snapshot_model = Snapshot

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        user = self._create_user(username='tester', email='tester@email.com')
        perm = Permission.objects.filter(codename__endswith='topology')
        user.user_permissions.add(*perm)
        self._create_org_user(user=user, organization=org, is_admin=True)
        self._create_node(
            label="node1", addresses=["192.168.0.1"], topology=t, organization=org
        )
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t, organization=org
        )
        self.client.force_login(user)

    @property
    def detail_url(self):
        t = self.topology_model.objects.first()
        return reverse('network_graph', args=[t.pk])

    @property
    def receive_url(self):
        t = self.topology_model.objects.first()
        path = reverse('receive_topology', args=[t.pk])
        return f'{path}?key=test'

    @property
    def snapshot_url(self):
        t = self.topology_model.objects.first()
        path = reverse('network_graph_history', args=[t.pk])
        return f'{path}?date={self.snapshot_date}'

    def _set_receive(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.strategy = 'receive'
        t.key = 'test'
        t.expiration_time = 0
        t.save()

    @property
    def snapshot_date(self):
        self.topology_model.objects.first().save_snapshot()
        return self.snapshot_model.objects.first().date

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.data['type'], 'NetworkCollection')
        self.assertEqual(len(response.data['collection']), 1)

    def test_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data['type'], 'NetworkGraph')

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data['collection']), 0)

    def test_detail_unpublished(self):
        self._unpublish()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

    def test_receive(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(self.receive_url, data, content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'data received successfully')
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    def test_receive_with_deprecated_url(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = self._load('static/netjson-1-link.json')
        t = self.topology_model.objects.first()
        path = reverse('receive_topology_deprecated', args=[t.pk])
        path = f'{path}?key=test'
        response = self.client.post(path, data=data, content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        expected_path = reverse('receive_topology', args=[t.pk])
        expected_path = f'{expected_path}?key=test'
        message = (
            'data received successfully. '
            'This URL is depercated and will be removed in '
            f'future versions, use {expected_path}'
        )
        self.assertEqual(response.data['detail'], message)
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    def test_receive_404(self):
        # topology is set to FETCH strategy
        response = self.client.post(self.receive_url, content_type='text/plain')
        self.assertEqual(response.status_code, 404)

    def test_receive_415(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url, data, content_type='application/xml'
        )
        self.assertEqual(response.status_code, 415)

    def test_receive_400_missing_key(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url.replace('?key=test', ''), data, content_type='text/plain'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('missing required', response.data['detail'])

    def test_receive_400_unrecognized_format(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = 'WRONG'
        response = self.client.post(self.receive_url, data, content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertIn('not recognized', response.data['detail'])

    def test_receive_403(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url.replace('?key=test', '?key=wrong'),
            data,
            content_type='text/plain',
        )
        self.assertEqual(response.status_code, 403)

    def test_receive_options(self):
        self._set_receive()
        response = self.client.options(self.receive_url)
        self.assertEqual(response.data['parses'], ['text/plain'])

    def test_snapshot(self):
        response = self.client.get(self.snapshot_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'NetworkGraph')

    def test_snapshot_missing_date_400(self):
        date = self.snapshot_date
        response = self.client.get(
            self.snapshot_url.replace('?date={0}'.format(date), '')
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'missing required "date" parameter')

    def test_snapshot_invalid_date_403(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace('?date={0}'.format(date), '?date=wrong-date')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'invalid date supplied')

    def test_snapshot_no_snapshot_404(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace('?date={0}'.format(date), '?date=2001-01-01')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('no snapshot found', response.data['detail'])

    def _test_api_with_unauthenticated_user(self, url):
        self.client.logout()
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(
            r.data['detail'], 'Authentication credentials were not provided.'
        )
        self.assertEqual(len(r.data), 1)

    def _test_api_with_not_a_manager_user(self, user, url, has_detail=True):
        OrganizationUser.objects.filter(user=user).delete()
        perm = Permission.objects.filter(codename__endswith='topology')
        user.user_permissions.add(*perm)
        self.client.force_login(user)
        r = self.client.get(url)
        if not has_detail:
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.data['type'], 'NetworkCollection')
            self.assertEqual(len(r.data['collection']), 0)
            self.assertNotEqual(Topology.objects.all().count(), 0)
        else:
            detail = (
                'User is not a manager of the organization to '
                'which the requested resource belongs.'
            )
            self.assertEqual(r.status_code, 403)
            self.assertEqual(r.data['detail'], detail)
            self.assertEqual(len(r.data), 1)

    def _test_api_with_not_permitted_user(self, user, url):
        t = self.topology_model.objects.first()
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        self.client.force_login(user)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(
            r.data['detail'], 'You do not have permission to perform this action.'
        )
        self.assertEqual(len(r.data), 1)

    def test_list_with_auth_enabled(self):
        user = self._create_user(username='list-user', email='list@email.com')
        with self.subTest('test api with unauthenticated user'):
            self._test_api_with_unauthenticated_user(self.list_url)

        with self.subTest('test api with not a permitted user'):
            self._test_api_with_not_permitted_user(user, self.list_url)

        with self.subTest('test api with not a member user'):
            self._test_api_with_not_a_manager_user(
                user, self.list_url, has_detail=False
            )

    def test_detail_with_auth_enabled(self):
        user = self._create_user(username='detail-user', email='detail@email.com')
        with self.subTest('test api with unauthenticated user'):
            self._test_api_with_unauthenticated_user(self.detail_url)

        with self.subTest('test api with not a permitted user'):
            self._test_api_with_not_permitted_user(user, self.detail_url)

        with self.subTest('test api with not a member user'):
            self._test_api_with_not_a_manager_user(user, self.detail_url)

    def test_snapshot_with_auth_enabled(self):
        user = self._create_user(username='snapshot-user', email='snapshot@email.com')
        with self.subTest('test api with unauthenticated user'):
            self._test_api_with_unauthenticated_user(self.snapshot_url)

        with self.subTest('test api with not a permitted user'):
            self._test_api_with_not_permitted_user(user, self.snapshot_url)

        with self.subTest('test api with not a member user'):
            self._test_api_with_not_a_manager_user(user, self.snapshot_url)

    def _successful_api_tests(self):
        with self.subTest('test list'):
            r = self.client.get(self.list_url)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.data['type'], 'NetworkCollection')
            self.assertEqual(len(r.data['collection']), 1)

        with self.subTest('test detail'):
            response = self.client.get(self.detail_url)
            self.assertEqual(response.data['type'], 'NetworkGraph')

        with self.subTest('test receive'):
            self._set_receive()
            self.node_model.objects.all().delete()
            data = self._load('static/netjson-1-link.json')
            response = self.client.post(
                self.receive_url, data, content_type='text/plain'
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['detail'], 'data received successfully')
            self.assertEqual(self.node_model.objects.count(), 2)
            self.assertEqual(self.link_model.objects.count(), 1)

        with self.subTest('test history'):
            response = self.client.get(self.snapshot_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['type'], 'NetworkGraph')

    @patch.object(APIView, 'get_permissions', return_value=[])
    @patch.object(APIView, 'get_authenticators', return_value=[])
    def test_api_with_auth_disabled(self, perm_mocked, auth_mocked):
        user = self._get_user(username='tester')
        self.client.logout()
        self._successful_api_tests()
        self.client.force_login(user)

    def test_superuser_with_api_auth_enabled(self):
        user = self._create_admin(username='superapi', email='superapi@email.com')
        self.client.force_login(user)
        self._successful_api_tests()

    @patch.object(APIView, 'get_permissions', return_value=[])
    @patch.object(APIView, 'get_authenticators', return_value=[])
    def test_superuser_with_api_auth_disabled(self, perm_mocked, auth_mocked):
        user = self._create_admin(username='superapi', email='superapi@email.com')
        self.client.force_login(user)
        self._successful_api_tests()
