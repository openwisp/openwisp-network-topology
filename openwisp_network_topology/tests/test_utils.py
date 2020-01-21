from django.test import TestCase
from django_netjsongraph.tests import CreateGraphObjectsMixin
from django_netjsongraph.tests.utils import TestUtilsMixin

from openwisp_users.models import Organization

from ..models import Link, Node, Snapshot, Topology
from . import CreateOrgMixin


class TestUtils(TestCase, TestUtilsMixin,
                CreateGraphObjectsMixin, CreateOrgMixin):
    topology_model = Topology
    node_model = Node
    link_model = Link
    snapshot_model = Snapshot

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(label="node1", addresses=["192.168.0.1"],
                          topology=t, organization=org)
        self._create_node(label="node2", addresses=["192.168.0.2"],
                          topology=t, organization=org)

    def _create_link(self, **kwargs):
        org = Organization.objects.first()
        options = dict(cost='1',
                       cost_text='one',
                       properties={},
                       organization=org)
        options.update(kwargs)
        link = self.link_model(**options)
        link.full_clean()
        link.save()
        return link

    def test_save_snapshot_all_method(self, **kwargs):
        org = self._create_org()
        options = dict(organization=org)
        options.update(**kwargs)
        super().test_save_snapshot_all_method(**options)
