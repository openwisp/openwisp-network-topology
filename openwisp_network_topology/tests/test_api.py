import swapper
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from openwisp_controller.tests.utils import TestAdminMixin

from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import AssertNumQueriesSubTestMixin

from .utils import CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin, UnpublishMixin

Link = swapper.load_model('topology', 'Link')
Node = swapper.load_model('topology', 'Node')
Snapshot = swapper.load_model('topology', 'Snapshot')
Topology = swapper.load_model('topology', 'Topology')
OrganizationUser = swapper.load_model('openwisp_users', 'OrganizationUser')


class TestApi(
    AssertNumQueriesSubTestMixin,
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
        self.assertEqual(response.data['results']['type'], 'NetworkCollection')
        self.assertEqual(len(response.data['results']['collection']), 1)

    def test_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data['type'], 'NetworkGraph')

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data['results']['collection']), 0)

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
            self.assertEqual(r.data['results']['type'], 'NetworkCollection')
            self.assertEqual(len(r.data['results']['collection']), 0)
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

    def test_modelpermission_class_with_change_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username='list-user', email='list@email.com')
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        change_perm = Permission.objects.filter(codename='change_topology')
        user.user_permissions.add(*change_perm)
        self.client.force_login(user)
        with self.subTest('List url'):
            url = self.list_url
            with self.assertNumQueries(8):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        with self.subTest('Detail url'):
            url = self.detail_url
            with self.assertNumQueries(8):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_modelpermission_class_with_view_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username='list-user', email='list@email.com')
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        view_perm = Permission.objects.filter(codename='view_topology')
        user.user_permissions.add(*view_perm)
        self.client.force_login(user)
        with self.subTest('List url'):
            url = self.list_url
            with self.assertNumQueries(8):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        with self.subTest('Detail url'):
            url = self.detail_url
            with self.assertNumQueries(8):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_modelpermission_class_with_no_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username='list-user', email='list@email.com')
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        self.client.force_login(user)
        with self.subTest('List url'):
            url = self.list_url
            with self.assertNumQueries(4):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
        with self.subTest('Detail url'):
            url = self.detail_url
            with self.assertNumQueries(4):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

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
            self.assertEqual(r.data['results']['type'], 'NetworkCollection')
            self.assertEqual(len(r.data['results']['collection']), 1)

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

    def test_superuser_with_api_auth_enabled(self):
        user = self._create_admin(username='superapi', email='superapi@email.com')
        self.client.force_login(user)
        self._successful_api_tests()


class TestNodeLinkApi(
    AssertNumQueriesSubTestMixin,
    CreateGraphObjectsMixin,
    TestAdminMixin,
    TestOrganizationMixin,
    TestCase,
):
    topology_model = Topology
    node_model = Node
    link_model = Link

    def setUp(self):
        super().setUp()
        self._login()

    def test_node_list_api(self):
        path = reverse('node_list')
        self.assertEqual(Node.objects.count(), 0)
        with self.assertNumQueries(3):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_node_list_filter_api(self):
        path = reverse('node_list')
        org1 = self._create_org(name='org1')
        t1 = self._create_topology(organization=self._get_org())
        t2 = self._create_topology(organization=org1)
        self._create_node(
            label='node1',
            addresses=['192.168.0.1'],
            topology=t1,
            organization=self._get_org(),
        )
        self._create_node(
            label='node2', addresses=['192.168.0.2'], topology=t2, organization=org1
        )
        view_perm = Permission.objects.filter(codename='view_node')
        user = self._get_user()
        user.user_permissions.add(*view_perm)
        OrganizationUser.objects.create(user=user, organization=org1, is_admin=True)
        self.client.force_login(user)
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(Node.objects.count(), 2)

    def test_node_create_api(self):
        path = reverse('node_list')
        t1 = self._create_topology(organization=self._get_org())
        data = {
            'topology': t1.pk,
            'label': 'test-node',
            'addresses': ['192.168.0.1'],
            'properties': {},
            'user_properties': {},
        }
        with self.assertNumQueries(8):
            response = self.client.post(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['topology'], t1.pk)
        self.assertEqual(response.data['label'], 'test-node')
        self.assertEqual(response.data['addresses'], ['192.168.0.1'])

    def test_node_detail_api(self):
        t1 = self._create_topology(organization=self._get_org())
        node1 = self._create_node(label='node1', addresses=['192.168.0.1'], topology=t1)
        path = reverse('node_detail', args=(node1.pk,))
        with self.assertNumQueries(3):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(node1.pk))
        self.assertEqual(response.data['topology'], t1.pk)
        self.assertEqual(response.data['label'], 'node1')

    def test_node_put_api(self):
        t1 = self._create_topology(organization=self._get_org())
        node1 = self._create_node(label='node1', addresses=['192.168.0.1'], topology=t1)
        data = {
            'topology': t1.pk,
            'label': 'change-node',
            'addresses': ['192.168.0.1', '192.168.0.2'],
            'properties': {},
            'user_properties': {},
        }
        path = reverse('node_detail', args=(node1.pk,))
        with self.assertNumQueries(9):
            response = self.client.put(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['label'], 'change-node')
        self.assertEqual(response.data['addresses'], ['192.168.0.1', '192.168.0.2'])

    def test_node_patch_api(self):
        t1 = self._create_topology(organization=self._get_org())
        node1 = self._create_node(label='node1', addresses=['192.168.0.1'], topology=t1)
        path = reverse('node_detail', args=(node1.pk,))
        data = {'label': 'change-node'}
        with self.assertNumQueries(8):
            response = self.client.patch(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['label'], 'change-node')

    def test_node_delete_api(self):
        t1 = self._create_topology(organization=self._get_org())
        node1 = self._create_node(label='node1', addresses=['192.168.0.1'], topology=t1)
        path = reverse('node_detail', args=(node1.pk,))
        with self.assertNumQueries(6):
            response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Node.objects.count(), 0)

    def test_link_list_api(self):
        path = reverse('link_list')
        with self.assertNumQueries(3):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_link_create_api(self):
        path = reverse('link_list')
        t = self._create_topology(organization=self._get_org())
        n1 = self._create_node(label='node1', topology=t)
        n2 = self._create_node(label='node2', topology=t)
        data = {
            'topology': t.pk,
            'source': n1.pk,
            'target': n2.pk,
            'cost': 1.0,
            'properties': {},
            'user_properties': {},
        }
        with self.assertNumQueries(12):
            response = self.client.post(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['topology'], t.pk)
        self.assertEqual(response.data['status'], 'up')
        self.assertEqual(response.data['source'], n1.pk)
        self.assertEqual(response.data['target'], n2.pk)

    def test_link_detail_api(self):
        t = self._create_topology(organization=self._get_org())
        n1 = self._create_node(label='node1', topology=t)
        n2 = self._create_node(label='node2', topology=t)
        l1 = self._create_link(topology=t, source=n1, target=n2)
        path = reverse('link_detail', args=(l1.pk,))
        with self.assertNumQueries(3):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(l1.pk))
        self.assertEqual(response.data['topology'], t.pk)
        self.assertEqual(response.data['source'], n1.pk)
        self.assertEqual(response.data['target'], n2.pk)

    def test_link_put_api(self):
        t = self._create_topology(organization=self._get_org())
        n1 = self._create_node(label='node1', topology=t)
        n2 = self._create_node(label='node2', topology=t)
        l1 = self._create_link(topology=t, source=n1, target=n2)
        path = reverse('link_detail', args=(l1.pk,))
        data = {
            'topology': t.pk,
            'source': n1.pk,
            'target': n2.pk,
            'cost': 21.0,
            'properties': {},
            'user_properties': {'user': 'tester'},
        }
        with self.assertNumQueries(15):
            response = self.client.put(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cost'], 21.0)
        self.assertEqual(response.data['properties'], {})
        self.assertEqual(response.data['user_properties'], {'user': 'tester'})

    def test_link_patch_api(self):
        t = self._create_topology(organization=self._get_org())
        n1 = self._create_node(label='node1', topology=t)
        n2 = self._create_node(label='node2', topology=t)
        l1 = self._create_link(topology=t, source=n1, target=n2)
        path = reverse('link_detail', args=(l1.pk,))
        data = {'cost': 50.0}
        with self.assertNumQueries(12):
            response = self.client.patch(path, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cost'], 50.0)

    def test_link_delete_api(self):
        t = self._create_topology(organization=self._get_org())
        n1 = self._create_node(label='node1', topology=t)
        n2 = self._create_node(label='node2', topology=t)
        l1 = self._create_link(topology=t, source=n1, target=n2)
        self.assertEqual(Link.objects.count(), 1)
        path = reverse('link_detail', args=(l1.pk,))
        with self.assertNumQueries(4):
            response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Link.objects.count(), 0)
