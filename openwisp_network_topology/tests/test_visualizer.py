import swapper
from django.test import TestCase
from django.urls import reverse

from .utils import CreateGraphObjectsMixin, CreateOrgMixin, UnpublishMixin

Node = swapper.load_model('topology', 'Node')
Topology = swapper.load_model('topology', 'Topology')


class TestVisualizer(UnpublishMixin, CreateOrgMixin, CreateGraphObjectsMixin, TestCase):
    topology_model = Topology
    node_model = Node

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label='node1', addresses=['192.168.0.1'], topology=t, organization=org
        )
        self._create_node(
            label='node2', addresses=['192.168.0.2'], topology=t, organization=org
        )

    def test_list(self):
        response = self.client.get(reverse('topology_list'))
        self.assertContains(response, 'TestNetwork')

    def test_detail(self):
        t = self.topology_model.objects.first()
        response = self.client.get(reverse('topology_detail', args=[t.pk]))
        self.assertContains(response, t.pk)
        # ensure switcher is present
        self.assertContains(response, 'njg-switcher')
        self.assertContains(response, 'njg-datepicker')

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(reverse('topology_list'))
        self.assertNotContains(response, 'TestNetwork')

    def test_detail_unpublished(self):
        self._unpublish()
        t = self.topology_model.objects.first()
        response = self.client.get(reverse('topology_detail', args=[t.pk]))
        self.assertEqual(response.status_code, 404)

    def test_detail_uuid_exception(self):
        """
        see https://github.com/netjson/django-netjsongraph/issues/4
        """
        t = self.topology_model.objects.first()
        response = self.client.get(
            reverse('topology_detail', args=['{0}-wrong'.format(t.pk)])
        )
        self.assertEqual(response.status_code, 404)
