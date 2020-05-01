import responses
from django.contrib.auth import get_user_model
from django.urls import reverse

from ...apps import OpenwispNetworkTopologyConfig as appconfig
from ...base.admin import AbstractTopologyAdmin
from ..utils import LoadMixin


class TestAdminMixin(LoadMixin):
    module = 'openwisp_network_topology'
    fixtures = ['test_users.json']

    @property
    def prefix(self):
        return 'admin:{0}'.format(appconfig.label)

    def setUp(self):
        user_model = get_user_model()
        self.client.force_login(user_model.objects.get(username='admin'))
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
        t = self.topology_model.objects.first()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[t.pk])
        response = self.client.get(path)
        self.assertContains(response, 'View on site')
        self.assertContains(response, t.get_absolute_url())

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
        self.assertContains(response, 'http://testserver/api/receive')
        # Change URL Test
        AbstractTopologyAdmin.receive_url_baseurl = 'http://changedurlbase'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, 'http://changedurlbase/api/receive')
        # Change URLConf Test
        AbstractTopologyAdmin.receive_url_urlconf = '{}.api.urls'.format(self.module)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-receive_url')
        self.assertContains(response, 'http://changedurlbase/receive')
        # Reset test options
        AbstractTopologyAdmin.receive_url_baseurl = None
        AbstractTopologyAdmin.receive_url_urlconf = None

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
        t = self.topology_model.objects.first()
        path = reverse('{0}_topology_change'.format(self.prefix), args=[t.pk])
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
