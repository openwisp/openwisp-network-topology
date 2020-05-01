from django.test import TestCase

from ..models import Node, Topology
from . import CreateGraphObjectsMixin, CreateOrgMixin
from .base.test_node import TestNodeMixin


class TestNode(TestNodeMixin, CreateGraphObjectsMixin, CreateOrgMixin, TestCase):
    topology_model = Topology
    node_model = Node
    maxDiff = 0

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label='node1', addresses=['192.168.0.1'], topology=t, organization=org
        )
        self._create_node(
            label='node2', addresses=['192.168.0.2'], topology=t, organization=org
        )
