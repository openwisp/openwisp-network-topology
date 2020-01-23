from django.test import TestCase
from django_netjsongraph.tests import CreateGraphObjectsMixin
from django_netjsongraph.tests.base.test_link import TestLinkMixin

from ..models import Link, Node, Topology
from . import CreateOrgMixin


class TestLink(TestLinkMixin, CreateOrgMixin,
               CreateGraphObjectsMixin, TestCase):
    topology_model = Topology
    node_model = Node
    link_model = Link

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(label="node1", addresses=["192.168.0.1"],
                          topology=t, organization=org)
        self._create_node(label="node2", addresses=["192.168.0.2"],
                          topology=t, organization=org)
