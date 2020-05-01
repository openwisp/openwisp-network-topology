from django.test import TestCase

from ..models import Node, Topology
from . import CreateGraphObjectsMixin, CreateOrgMixin
from .base.test_visualizer import TestVisualizerMixin


class TestVisualizer(
    TestVisualizerMixin, CreateOrgMixin, CreateGraphObjectsMixin, TestCase
):
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
