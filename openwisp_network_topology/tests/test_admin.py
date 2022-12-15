import re

import responses
import swapper
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from openwisp_users.tests.utils import TestMultitenantAdminMixin, TestOrganizationMixin
from openwisp_utils.tests import capture_any_output

from ..admin import TopologyAdmin
from .utils import CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin

Link = swapper.load_model('topology', 'Link')
Node = swapper.load_model('topology', 'Node')
Topology = swapper.load_model('topology', 'Topology')
OrganizationUser = swapper.load_model('openwisp_users', 'OrganizationUser')
Organization = swapper.load_model('openwisp_users', 'Organization')


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

    @capture_any_output()
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
        receive_path = f'network-topology/topology/{t.pk}/receive/'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, f'http://testserver/api/v1/{receive_path}')
        # Change URL Test
        TopologyAdmin.receive_url_baseurl = 'http://changedurlbase'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, f'http://changedurlbase/api/v1/{receive_path}')
        # Change URLConf Test
        TopologyAdmin.receive_url_urlconf = '{}.{}'.format(
            self.module, self.api_urls_path
        )
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, f'http://changedurlbase/{receive_path}')
        # Reset test options
        TopologyAdmin.receive_url_baseurl = None
        TopologyAdmin.receive_url_urlconf = None

    def test_node_change_form(self):
        n = self.node_model.objects.first()
        path = reverse('{0}_node_change'.format(self.prefix), args=[n.pk])
        response = self.client.get(path)
        self.assertContains(response, 'Links to other nodes')
        self.assertNotContains(response, 'organization_id')
        self.assertContains(response, n.topology.organization.name)

    def test_node_change_list_queries(self):
        path = reverse('{0}_node_changelist'.format(self.prefix))
        with self.assertNumQueries(5):
            self.client.get(path)

    def test_link_change_list_queries(self):
        t = Topology.objects.first()
        n1 = self._create_node(label='node1org1', topology=t)
        n2 = self._create_node(label='node2org1', topology=t)
        self._create_link(topology=t, source=n1, target=n2)
        path = reverse('{0}_link_changelist'.format(self.prefix))
        with self.assertNumQueries(5):
            self.client.get(path)

    def test_link_change_form(self):
        t = Topology.objects.first()
        n1 = self._create_node(label='node1org1', topology=t)
        n2 = self._create_node(label='node2org1', topology=t)
        link = self._create_link(topology=t, source=n1, target=n2)
        path = reverse('{0}_link_change'.format(self.prefix), args=[link.pk])
        response = self.client.get(path)
        self.assertNotContains(response, 'organization_id')
        self.assertContains(response, link.topology.organization.name)

    def test_node_add(self):
        path = reverse('{0}_node_add'.format(self.prefix))
        response = self.client.get(path)
        self.assertNotContains(response, 'Links to other nodes')

    def test_topology_change_form(self):
        topology = self.topology_model.objects.first()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[topology.pk])
        response = self.client.get(path)
        self.assertContains(response, 'View topology graph')
        self.assertContains(
            response, '<div class="readonly">{0}</div>'.format(topology.pk)
        )

    def test_topology_visualize_view(self):
        t = self.topology_model.objects.first()
        path = reverse('{0}_topology_visualize'.format(self.prefix), args=[t.pk])
        response = self.client.get(path)
        self.assertContains(response, 'new NetJSONGraph(')

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

    def _test_properties_field(self, model, obj):
        with self.subTest('test old properties readonly'):
            content = 'readonly_properties">'
            r = self.client.get(reverse(f'{self.prefix}_{model}_add'))
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, content)

        with self.subTest('test old properties display in list'):
            path = reverse(f'{self.prefix}_{model}_change', args=[obj.pk])
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200)
            content = '<p><strong>Gateway</strong>: False</p>'
            self.assertContains(r, content)

        with self.subTest('test user properties diplay in flat json widgets'):
            r = self.client.get(reverse(f'{self.prefix}_{model}_add'))
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'flat-json-user_properties')

    def test_node_user_properties_field(self):
        t = Topology.objects.first()
        n = self._create_node(label='node1org1', topology=t)
        n.properties = {'gateway': False}
        n.full_clean()
        n.save()
        self._test_properties_field('node', n)

    def test_link_user_properties_field(self):
        t = Topology.objects.first()
        n1 = self._create_node(label='node1org1', topology=t)
        n2 = self._create_node(label='node2org1', topology=t)
        li = self._create_link(topology=t, source=n1, target=n2)
        li.properties = {'gateway': False}
        li.full_clean()
        li.save()
        self._test_properties_field('link', li)

    def test_admin_menu_groups(self):
        # Test menu group (openwisp-utils menu group) for Topology and Link
        # and Node
        self.client.force_login(self.user_model.objects.get(username='admin'))
        response = self.client.get(reverse('admin:index'))
        models = ['topology', 'node', 'link']
        for model in models:
            with self.subTest('test menu group link for {model} model'):
                url = reverse(f'admin:{self.app_label}_{model}_changelist')
                self.assertContains(response, f'class="mg-link" href="{url}"')
        with self.subTest('test "networking topology" group is registered'):
            self.assertContains(
                response,
                '<div class="mg-dropdown-label">Network Topology </div>',
                html=True,
            )


class TestMultitenantAdmin(
    CreateGraphObjectsMixin, TestMultitenantAdminMixin, TestOrganizationMixin, TestCase
):
    app_label = 'topology'
    topology_model = Topology
    node_model = Node
    link_model = Link
    org_model = Organization
    user_model = get_user_model()

    def _create_multitenancy_test_env(self):
        org1 = self._create_org(name='test1org')
        org2 = self._create_org(name='test2org')
        inactive = self._create_org(name='inactive-org', is_active=False)
        operator = self._create_operator(organizations=[org1, inactive])
        administrator = self._create_administrator(organizations=[org1, inactive])
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
            administrator=administrator,
        )
        return data

    def _test_topology_autocomplete_filter(self, url_reverse=None, payload=None):
        url = reverse(url_reverse)

        with self.subTest('test superadmin topology autocomplete filter'):
            user = self.user_model.objects.filter(
                is_superuser=True, is_staff=True
            ).first()
            self.client.force_login(user)
            response = self.client.get(url, payload)
            self.assertEqual(response.status_code, 200)
            for option in response.json()['results']:
                assert option['id'] in [
                    str(id)
                    for id in self.topology_model.objects.values_list('id', flat=True)
                ]

        with self.subTest('test non superadmin topology autocomplete filter'):
            user = self.user_model.objects.get(username='administrator')
            self.client.force_login(user)
            response = self.client.get(url, payload)
            self.assertEqual(response.status_code, 200)
            topologies = self.topology_model.objects.filter(
                organization=user.organizations_managed[0]
            )
            for option in response.json()['results']:
                assert option['id'] in [
                    str(id) for id in topologies.values_list('id', flat=True)
                ]

    def test_topology_queryset(self):
        data = self._create_multitenancy_test_env()
        perm = Permission.objects.get_by_natural_key(
            'delete_topology', self.app_label, self.topology_model.__name__.lower()
        )
        data['operator'].user_permissions.remove(perm)
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_topology_changelist'),
            visible=[data['t1'].label, data['org1'].name],
            hidden=[data['t2'].label, data['org2'].name, data['t3_inactive'].label],
        )

    def test_topology_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._create_topology(label='special', organization=data['org1'])
        url = reverse('admin:autocomplete')
        payload = {
            'app_label': self.app_label,
            'model_name': self.app_label,
            'field_name': 'organization',
        }

        with self.subTest(
            'test superadmin add topology organization autocomplete filter'
        ):
            user = self.user_model.objects.filter(
                is_superuser=True, is_staff=True
            ).first()
            self.client.force_login(user)
            response = self.client.get(url, payload)
            self.assertEqual(response.status_code, 200)
            for option in response.json()['results']:
                assert option['id'] in [
                    str(id)
                    for id in self.org_model.objects.values_list('id', flat=True)
                ]

        with self.subTest(
            'test non superadmin add topology organization autocomplete filter'
        ):
            user = self.user_model.objects.get(username='administrator')
            self.client.force_login(user)
            response = self.client.get(url, payload)
            self.assertEqual(response.status_code, 200)
            for option in response.json()['results']:
                assert option['id'] in [str(id) for id in user.organizations_managed]
                assert option['id'] not in self.org_model.objects.exclude(
                    pk__in=user.organizations_managed
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
        self._create_multitenancy_test_env()
        self._login(username='operator', password='tester')
        response = self.client.get(reverse(f'admin:{self.app_label}_node_add'))
        self.assertNotContains(response, 'organization_id')

    def test_link_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse(f'admin:{self.app_label}_link_changelist'),
            visible=[str(data['l1']), data['org1'].name],
            hidden=[str(data['l2']), data['org2'].name, str(data['l3_inactive'])],
        )

    def test_link_organization_fk_queryset(self):
        self._create_multitenancy_test_env()
        self._login(username='operator', password='tester')
        response = self.client.get(reverse(f'admin:{self.app_label}_link_add'))
        self.assertNotContains(response, 'organization_id')

    def test_node_topology_fk_queryset(self):
        self._create_multitenancy_test_env()
        payload = {
            'app_label': self.app_label,
            'model_name': 'node',
            'field_name': self.app_label,
        }
        self._test_topology_autocomplete_filter(
            url_reverse='admin:autocomplete', payload=payload
        )

    def test_link_topology_fk_queryset(self):
        self._create_multitenancy_test_env()
        payload = {
            'app_label': self.app_label,
            'model_name': 'link',
            'field_name': self.app_label,
        }
        self._test_topology_autocomplete_filter(
            url_reverse='admin:autocomplete', payload=payload
        )

    def test_node_topology_filter(self):
        data = self._create_multitenancy_test_env()
        self._create_topology(label='special', organization=data['org1'])
        payload = {
            'app_label': self.app_label,
            'model_name': 'node',
            'field_name': self.app_label,
        }
        self._test_topology_autocomplete_filter(
            url_reverse='admin:ow-auto-filter', payload=payload
        )

    def test_link_topology_filter(self):
        data = self._create_multitenancy_test_env()
        self._create_topology(label='special', organization=data['org1'])
        payload = {
            'app_label': self.app_label,
            'model_name': 'link',
            'field_name': self.app_label,
        }
        self._test_topology_autocomplete_filter(
            url_reverse='admin:ow-auto-filter', payload=payload
        )
