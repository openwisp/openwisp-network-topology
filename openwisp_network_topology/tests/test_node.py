from django.test import TestCase
from django_netjsongraph.tests import CreateGraphObjectsMixin
from django_netjsongraph.tests.base.test_node import TestNodeMixin

from ..models import Node, Topology
from . import CreateOrgMixin


class TestNode(TestNodeMixin, CreateGraphObjectsMixin, CreateOrgMixin, TestCase):
    topology_model = Topology
    node_model = Node
    maxDiff = 0

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(label="node1", addresses=["192.168.0.1"],
                          topology=t, organization=org)
        self._create_node(label="node2", addresses=["192.168.0.2"],
                          topology=t, organization=org)
