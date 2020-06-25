import swapper
from django.test import TestCase
from rest_framework.utils.encoders import JSONEncoder

from .utils import CreateGraphObjectsMixin, CreateOrgMixin

Node = swapper.load_model('topology', 'Node')
Topology = swapper.load_model('topology', 'Topology')


class TestNode(CreateGraphObjectsMixin, CreateOrgMixin, TestCase):
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

    def test_str(self):
        n = self.node_model(addresses=['192.168.0.1'], label='test node')
        self.assertIsInstance(str(n), str)

    def test_clean_properties(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            addresses=['192.168.0.1'], label='test node', properties=None
        )
        n.full_clean()
        self.assertEqual(n.properties, {})

    def test_node_address_single(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            addresses=['192.168.0.1'], label='test node', properties=None
        )
        n.full_clean()
        n.save()
        self.assertEqual(n.addresses[0], '192.168.0.1')
        self.assertEqual(n.addresses, ['192.168.0.1'])

    def test_node_address_multiple(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label='test node',
            addresses=['192.168.0.1', '10.0.0.1', '10.0.0.2', '10.0.0.3'],
        )
        self.assertEqual(
            n.addresses, ['192.168.0.1', '10.0.0.1', '10.0.0.2', '10.0.0.3']
        )

    def test_node_local_addresses(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label='test node', addresses=['192.168.0.1', '10.0.0.1', '10.0.0.2']
        )
        self.assertEqual(n.local_addresses, ['10.0.0.1', '10.0.0.2'])

    def test_node_name(self):
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=['192.168.0.1', '10.0.0.1'])
        self.assertEqual(n.name, '192.168.0.1')
        n.label = 'test node'
        self.assertEqual(n.name, 'test node')

    def test_node_without_name(self):
        # According to the RFC, a node MAY not have name nor local_addresses defined
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=[])
        self.assertEqual(n.name, '')

    def test_json(self):
        t = self.topology_model.objects.first()
        n = t._create_node(
            label='test node',
            addresses=['192.168.0.1', '10.0.0.1'],
            properties={"gateway": True},
        )
        self.assertEqual(
            dict(n.json(dict=True)),
            {
                'id': '192.168.0.1',
                'label': 'test node',
                'local_addresses': ['10.0.0.1'],
                'properties': {
                    'gateway': True,
                    'created': JSONEncoder().default(n.created),
                    'modified': JSONEncoder().default(n.modified),
                },
            },
        )
        self.assertIsInstance(n.json(), str)

    def test_get_from_address(self):
        t = self.topology_model.objects.first()
        n = t._create_node(addresses=['192.168.0.1', '10.0.0.1'])
        n.full_clean()
        n.save()
        self.assertIsInstance(
            self.node_model.get_from_address('192.168.0.1', t), self.node_model
        )
        self.assertIsInstance(
            self.node_model.get_from_address('10.0.0.1', t), self.node_model
        )
        self.assertIsNone(self.node_model.get_from_address('wrong', t))

    def test_count_address(self):
        t = self.topology_model.objects.first()
        self.assertEqual(self.node_model.count_address('192.168.0.1', t), 1)
        self.assertEqual(self.node_model.count_address('0.0.0.0', t), 0)

    def test_count_address_issue_58(self):
        t = self.topology_model.objects.first()
        n1 = t._create_node(addresses=['Benz_Kalloni'])
        n1.full_clean()
        n1.save()
        n2 = t._create_node(addresses=['Kalloni'])
        n2.full_clean()
        n2.save()
        self.assertEqual(self.node_model.count_address('Benz_Kalloni', t), 1)
        self.assertEqual(self.node_model.count_address('Kalloni', t), 1)
