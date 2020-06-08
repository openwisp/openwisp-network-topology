import re

import responses
import swapper
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from openwisp_users.tests.utils import TestMultitenantAdminMixin, TestOrganizationMixin

from ..admin import TopologyAdmin
from .utils import CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin

Link = swapper.load_model('topology', 'Link')
Node = swapper.load_model('topology', 'Node')
Topology = swapper.load_model('topology', 'Topology')


class TestAdmin(CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin, TestCase):
    module = 'openwisp_network_topology'
    app_label = 'topology'
    topology_model = Topology
    link_model = Link
    node_model = Node
    user_model = get_user_model()
    fixtures = ['test_users.json']
    api_urls_path = 'api.urls'

    @property
    def prefix(self):
        return 'admin:{0}'.format(self.app_label)

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label='node1', addresses=['192.168.0.1'], topology=t, organization=org
        )
        self._create_node(
            label='node2', addresses=['192.168.0.2'], topology=t, organization=org
        )
        self.client.force_login(self.user_model.objects.get(username='admin'))
        self.changelist_path = reverse('{0}_topology_changelist'.format(self.prefix))

    def test_unpublish_selected(self):
        t = self.topology_model.objects.first()
        self.assertEqual(t.published, True)
        self.client.post(
            self.changelist_path,
            {'action': 'unpublish_selected', '_selected_action': str(t.pk)},
        )
        t.refresh_from_db()
        self.assertEqual(t.published, False)

    def test_publish_selected(self):
        t = self.topology_model.objects.first()
        t.published = False
        t.save()
        self.client.post(
            self.changelist_path,
            {'action': 'publish_selected', '_selected_action': str(t.pk)},
        )
        t.refresh_from_db()
        self.assertEqual(t.published, True)

    @responses.activate
    def test_update_selected(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body=self._load('static/netjson-1-link.json'),
            content_type='application/json',
        )
        self.node_model.objects.all().delete()
        self.client.post(
            self.changelist_path,
            {'action': 'update_selected', '_selected_action': str(t.pk)},
        )
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    @responses.activate
    def test_update_selected_failed(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body='{"error": "not found"}',
            status=404,
            content_type='application/json',
        )
        self.node_model.objects.all().delete()
        response = self.client.post(
            self.changelist_path,
            {'action': 'update_selected', '_selected_action': str(t.pk)},
            follow=True,
        )
        self.assertEqual(self.node_model.objects.count(), 0)
        self.assertEqual(self.link_model.objects.count(), 0)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.tags, 'error')
        self.assertIn('not updated', message.message)

    def test_topology_viewonsite(self):
        topology = self.topology_model.objects.first()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[topology.pk])
        response = self.client.get(path)
        self.assertContains(response, 'View on site')
        # Pattern for the link
        pattern = '{0}{1}'.format(r'/admin/r/[0-9][0-9]?/', f'{topology.pk}')
        self.assertTrue(bool(re.compile(pattern).search(str(response.content))))

    def test_topology_receive_url(self):
        t = self.topology_model.objects.first()
        t.strategy = 'receive'
        t.save()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[t.pk])
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')

    def test_custom_topology_receive_url(self):
        t = self.topology_model.objects.first()
        t.strategy = 'receive'
        t.save()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[t.pk])
        # No change in URL Test
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, 'http://testserver/api/v1/receive')
        # Change URL Test
        TopologyAdmin.receive_url_baseurl = 'http://changedurlbase'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, 'http://changedurlbase/api/v1/receive')
        # Change URLConf Test
        TopologyAdmin.receive_url_urlconf = '{}.{}'.format(
            self.module, self.api_urls_path
        )
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, 'http://changedurlbase/receive')
        # Reset test options
        TopologyAdmin.receive_url_baseurl = None
        TopologyAdmin.receive_url_urlconf = None

    def test_node_change_form(self):
        n = self.node_model.objects.first()
        path = reverse('{0}_node_change'.format(self.prefix), args=[n.pk])
        response = self.client.get(path)
        self.assertContains(response, 'Links to other nodes')

    def test_node_add(self):
        path = reverse('{0}_node_add'.format(self.prefix))
        response = self.client.get(path)
        self.assertNotContains(response, 'Links to other nodes')

    def test_topology_visualize_button(self):
        topology = self.topology_model.objects.first()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[topology.pk])
        response = self.client.get(path)
        self.assertContains(response, 'View topology graph')

    def test_topology_visualize_view(self):
        t = self.topology_model.objects.first()
        path = reverse('{0}_topology_visualize'.format(self.prefix), args=[t.pk])
        response = self.client.get(path)
        self.assertContains(response, 'd3.netJsonGraph(')

    def test_update_selected_receive_topology(self):
        t = self.topology_model.objects.first()
        t.label = 'test receive'
        t.parser = 'netdiff.NetJsonParser'
        t.strategy = 'receive'
        t.save()
        response = self.client.post(
            self.changelist_path,
            {'action': 'update_selected', '_selected_action': str(t.pk)},
            follow=True,
        )
        message = list(response.context['messages'])[0]
        self.assertEqual('warning', message.tags)
        self.assertIn('1 topology was ignored', message.message)


class TestMultitenantAdmin(
    CreateGraphObjectsMixin, TestMultitenantAdminMixin, TestOrganizationMixin, TestCase
):
    app_label = 'topology'
    topology_model = Topology
    node_model = Node
    link_model = Link

    operator_permission_filters = [
        {'codename__endswith': 'topology'},
        {'codename__endswith': 'node'},
        {'codename__endswith': 'link'},
    ]

    def _create_multitenancy_test_env(self):
        org1 = self._create_org(name='test1org')
        org2 = self._create_org(name='test2org')
        inactive = self._create_org(name='inactive-org', is_active=False)
        operator = self._create_operator(organizations=[org1, inactive])
        t1 = self._create_topology(label='topology1org', organization=org1)
        t2 = self._create_topology(label='topology2org', organization=org2)
        t3 = self._create_topology(label='topology3org', organization=inactive)
        n11 = self._create_node(label='node1org1', topology=t1, organization=org1)
        n12 = self._create_node(label='node2org1', topology=t1, organization=org1)
        n21 = self._create_node(label='node1org2', topology=t2, organization=org2)
        n22 = self._create_node(label='node2org2', topology=t2, organization=org2)
        n31 = self._create_node(
            label='node1inactive', topology=t3, organization=inactive
        )
        n32 = self._create_node(
            label='node2inactive', topology=t3, organization=inactive
        )
        l1 = self._create_link(topology=t1, organization=org1, source=n11, target=n12)
        l2 = self._create_link(topology=t2, organization=org2, source=n21, target=n22)
        l3 = self._create_link(
            topology=t3, organization=inactive, source=n31, target=n32
        )
        data = dict(
            t1=t1,
            t2=t2,
            t3_inactive=t3,
            n11=n11,
            n12=n12,
            l1=l1,
            n21=n21,
            n22=n22,
            l2=l2,
            n31=n31,
            n32=n32,
            l3_inactive=l3,
            org1=org1,
            org2=org2,
            inactive=inactive,
            operator=operator,
        )
        return data

    def test_topology_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_topology_changelist'),
            visible=[data['t1'].label, data['org1'].name],
            hidden=[data['t2'].label, data['org2'].name, data['t3_inactive'].label],
        )

    def test_topology_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_topology_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True,
        )

    def test_node_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_node_changelist'),
            visible=[data['n11'].label, data['n12'].label, data['org1'].name],
            hidden=[
                data['n21'].label,
                data['n22'].label,
                data['org2'].name,
                data['n31'].label,
                data['n32'].label,
                data['inactive'],
            ],
        )

    def test_node_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_node_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True,
        )

    def test_link_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_link_changelist'),
            visible=[str(data['l1']), data['org1'].name],
            hidden=[str(data['l2']), data['org2'].name, str(data['l3_inactive'])],
        )

    def test_link_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_link_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True,
        )

    def test_node_topology_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_node_add'),
            visible=[data['t1'].label],
            hidden=[data['t2'].label, data['t3_inactive'].label],
        )

    def test_link_topology_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_link_add'),
            visible=[data['t1'].label],
            hidden=[data['t2'].label, data['t3_inactive'].label],
        )

    def test_node_topology_filter(self):
        data = self._create_multitenancy_test_env()
        t_special = self._create_topology(label='special', organization=data['org1'])
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_node_changelist'),
            visible=[data['t1'].label, t_special.label],
            hidden=[data['t2'].label, data['t3_inactive'].label],
        )

    def test_link_topology_filter(self):
        data = self._create_multitenancy_test_env()
        t_special = self._create_topology(label='special', organization=data['org1'])
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_link_changelist'),
            visible=[data['t1'].label, t_special.label],
            hidden=[data['t2'].label, data['t3_inactive'].label],
        )
