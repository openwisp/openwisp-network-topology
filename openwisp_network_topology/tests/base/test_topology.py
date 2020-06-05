from datetime import timedelta

import responses
from django.core.exceptions import ValidationError
from freezegun import freeze_time
from netdiff import OlsrParser

from ..utils import LoadMixin


class TestTopologyMixin(LoadMixin):
    maxDiff = None

    def _get_nodes(self):
        return self.node_model.objects.all()

    def _set_receive(self, expiration_time=0, parser='netdiff.NetJsonParser'):
        t = self.topology_model.objects.first()
        t.parser = parser
        t.strategy = 'receive'
        t.key = 'test'
        t.expiration_time = expiration_time
        t.save()
        return t

    def test_str(self):
        t = self.topology_model.objects.first()
        self.assertIsInstance(str(t), str)

    def test_parser(self):
        t = self.topology_model.objects.first()
        self.assertIs(t.parser_class, OlsrParser)

    def test_json_empty(self):
        t = self.topology_model.objects.first()
        self.node_model.objects.all().delete()
        graph = t.json(dict=True)
        self.assertDictEqual(
            graph,
            {
                'type': 'NetworkGraph',
                'protocol': 'OLSR',
                'version': '0.8',
                'metric': 'ETX',
                'label': t.label,
                'id': str(t.id),
                'parser': t.parser,
                'created': t.created,
                'modified': t.modified,
                'nodes': [],
                'links': [],
            },
        )

    def test_json(self):
        node1, node2 = self._get_nodes()
        t = self.topology_model.objects.first()
        node3 = t._create_node(addresses=['192.168.0.3'], label='node3')
        node3.save()
        link = t._create_link(source=node1, target=node2, cost=1)
        link.save()
        l2 = t._create_link(source=node1, target=node3, cost=1)
        l2.save()
        graph = t.json(dict=True)
        self.assertDictEqual(
            dict(graph),
            {
                'type': 'NetworkGraph',
                'protocol': 'OLSR',
                'version': '0.8',
                'metric': 'ETX',
                'label': t.label,
                'id': str(t.id),
                'parser': t.parser,
                'created': t.created,
                'modified': t.modified,
                'nodes': [
                    dict(node1.json(dict=True)),
                    dict(node2.json(dict=True)),
                    dict(node3.json(dict=True)),
                ],
                'links': [dict(link.json(dict=True)), dict(l2.json(dict=True))],
            },
        )
        self.assertIsInstance(t.json(), str)

    @responses.activate
    def test_empty_diff(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body=t.json(),
            content_type='application/json',
        )
        self.assertDictEqual(
            t.diff(), {'added': None, 'removed': None, 'changed': None}
        )

    @responses.activate
    def test_update_all_attributes(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body=self._load('static/netjson-1-link.json'),
            content_type='application/json',
        )
        t.protocol = None
        t.version = None
        t.metric = None
        t.update()
        t.refresh_from_db()
        self.assertEqual(t.protocol, 'OLSR')
        self.assertEqual(t.version, '0.8')
        self.assertEqual(t.metric, 'ETX')

    @responses.activate
    def test_update_added(self):
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
        t.update()
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        node1 = self.node_model.objects.get(addresses__contains='"192.168.0.1"')
        node2 = self.node_model.objects.get(addresses__contains='"192.168.0.2"')
        self.assertEqual(node1.local_addresses, ['10.0.0.1'])
        self.assertEqual(node1.properties, {'gateway': True})
        link = self.link_model.objects.first()
        self.assertIn(link.source, [node1, node2])
        self.assertIn(link.target, [node1, node2])
        self.assertEqual(link.cost, 1.0)
        self.assertEqual(link.properties, {'pretty': True})
        # ensure repeating the action is idempotent
        t.update()
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    @responses.activate
    def test_update_changed(self):
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
        t.update()
        link = self.link_model.objects.first()
        # now change
        t.url = t.url.replace('9090', '9091')
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9091',
            body=self._load('static/netjson-2-links.json'),
            content_type='application/json',
        )
        t.update()
        link.refresh_from_db()
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        self.assertEqual(link.cost, 1.5)

    @responses.activate
    def test_update_removed(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body=self._load('static/netjson-2-links.json'),
            content_type='application/json',
        )
        self.node_model.objects.all().delete()
        t.update()
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        # now change
        t.url = t.url.replace('9090', '9091')
        t.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9091',
            body=self._load('static/netjson-1-link.json'),
            content_type='application/json',
        )
        t.update()
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.filter(status='down').count(), 1)
        link = self.link_model.objects.filter(status='down').first()
        self.assertIn('192.168.0.3', [link.source.netjson_id, link.target.netjson_id])
        self.assertEqual(link.cost, 2.0)

    @responses.activate
    def test_update_status_existing_link(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.save()
        n1 = self.node_model.objects.all()[0]
        n2 = self.node_model.objects.all()[1]
        link = t._create_link(
            source=n1, target=n2, cost=1, status='down', properties={'pretty': True}
        )
        link.full_clean()
        link.save()
        responses.add(
            responses.GET,
            'http://127.0.0.1:9090',
            body=self._load('static/netjson-1-link.json'),
            content_type='application/json',
        )
        t.update()
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        link.refresh_from_db()
        self.assertEqual(link.status, 'up')

    def test_topology_url_empty(self):
        t = self.topology_model(
            label='test', parser='netdiff.NetJsonParser', strategy='fetch'
        )
        with self.assertRaises(ValidationError):
            t.full_clean()

    def test_topology_key_empty(self):
        t = self.topology_model(
            label='test', parser='netdiff.NetJsonParser', strategy='receive', key=''
        )
        with self.assertRaises(ValidationError):
            t.full_clean()

    def _test_receive_added(self, expiration_time=0):
        self.node_model.objects.all().delete()
        t = self._set_receive(expiration_time)
        data = self._load('static/netjson-1-link.json')
        t.receive(data)
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        node1 = self.node_model.objects.get(addresses__contains='"192.168.0.1"')
        node2 = self.node_model.objects.get(addresses__contains='"192.168.0.2"')
        self.assertEqual(node1.local_addresses, ['10.0.0.1'])
        self.assertEqual(node1.properties, {'gateway': True})
        link = self.link_model.objects.first()
        self.assertIn(link.source, [node1, node2])
        self.assertIn(link.target, [node1, node2])
        self.assertEqual(link.cost, 1.0)
        self.assertEqual(link.properties, {'pretty': True})
        # ensure repeating the action is idempotent
        t.receive(data)
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    def test_receive_added(self):
        self._test_receive_added()

    def _test_receive_changed(self, expiration_time=0):
        t = self._set_receive(expiration_time)
        self.node_model.objects.all().delete()
        data = self._load('static/netjson-1-link.json')
        t.receive(data)
        link = self.link_model.objects.first()
        # now change
        data = self._load('static/netjson-2-links.json')
        t.receive(data)
        link.refresh_from_db()
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        self.assertEqual(link.cost, 1.5)

    def test_receive_changed(self):
        self._test_receive_changed()

    def test_receive_removed(self):
        t = self._set_receive()
        self.node_model.objects.all().delete()
        data = self._load('static/netjson-2-links.json')
        t.receive(data)
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        # now change
        data = self._load('static/netjson-1-link.json')
        t.receive(data)
        self.assertEqual(self.node_model.objects.count(), 3)
        self.assertEqual(self.link_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.filter(status='down').count(), 1)
        link = self.link_model.objects.filter(status='down').first()
        self.assertIn('192.168.0.3', [link.source.netjson_id, link.target.netjson_id])
        self.assertEqual(link.cost, 2.0)

    def test_receive_status_existing_link(self):
        t = self._set_receive()
        n1 = self.node_model.objects.all()[0]
        n2 = self.node_model.objects.all()[1]
        link = t._create_link(
            source=n1, target=n2, cost=1, status='down', properties={'pretty': True}
        )
        link.full_clean()
        link.save()
        data = self._load('static/netjson-1-link.json')
        t.receive(data)
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        link.refresh_from_db()
        self.assertEqual(link.status, 'up')

    def test_multiple_receive_added(self):
        self._test_receive_added(expiration_time=50)

    def test_multiple_receive_changed(self):
        self._test_receive_changed(expiration_time=50)

    def test_multiple_receive_removed(self):
        with freeze_time() as frozen_time:
            t = self._set_receive(expiration_time=0.1)
            data = self._load('static/netjson-2-links.json')
            for sleep_time in [0, 0.2, 0.1]:
                frozen_time.tick(timedelta(seconds=sleep_time))
                t.receive(data)
                self.assertEqual(self.node_model.objects.count(), 3)
                self.assertEqual(self.link_model.objects.count(), 2)
                self.assertEqual(
                    self.link_model.objects.filter(status='down').count(), 0
                )
            # receive change
            data = self._load('static/netjson-1-link.json')
            t.receive(data)
            self.assertEqual(self.node_model.objects.count(), 3)
            self.assertEqual(self.link_model.objects.count(), 2)
            # expiration_time has not expired
            self.assertEqual(self.link_model.objects.filter(status='down').count(), 0)
            # expiration_time has now expired for 1 link
            frozen_time.tick(timedelta(seconds=0.2))
            t.receive(data)
            self.assertEqual(self.link_model.objects.filter(status='down').count(), 1)
            link = self.link_model.objects.filter(status='down').first()
            self.assertIn(
                '192.168.0.3', [link.source.netjson_id, link.target.netjson_id]
            )
            self.assertEqual(link.cost, 2.0)

    def test_multiple_receive_split_network(self):
        def _assert_split_topology(self, topology):
            self.assertEqual(self.node_model.objects.count(), 4)
            self.assertEqual(self.link_model.objects.filter(status='up').count(), 2)
            self.assertEqual(self.link_model.objects.filter(status='down').count(), 0)
            link = self.link_model.get_from_nodes(
                '192.168.0.1', '192.168.0.2', topology
            )
            self.assertIsNotNone(link)
            self.assertEqual(link.status, 'up')
            self.assertEqual(link.cost, 1.0)
            link = self.link_model.get_from_nodes(
                '192.168.0.10', '192.168.0.20', topology
            )
            self.assertIsNotNone(link)
            self.assertEqual(link.status, 'up')
            self.assertEqual(link.cost, 1.1)

        with freeze_time() as frozen_time:
            self.node_model.objects.all().delete()
            t = self._set_receive(expiration_time=0.5)
            network1 = self._load('static/netjson-1-link.json')
            network2 = self._load('static/split-network.json')
            t.receive(network1)
            t.receive(network2)
            _assert_split_topology(self, t)
            for sleep_time in [0.1, 0.25, 0.3]:
                frozen_time.tick(timedelta(seconds=sleep_time))
                t.receive(network1)
                _assert_split_topology(self, t)
                frozen_time.tick(timedelta(seconds=sleep_time))
                t.receive(network2)
                _assert_split_topology(self, t)

    def test_very_long_addresses(self):
        """
        see https://github.com/netjson/django-netjsongraph/issues/6
        """
        t = self._set_receive()
        data = self._load('static/very-long-addresses.json')
        t.receive(data)
        n = self.node_model.get_from_address('2001:4e12:452a:1:172::10', t)
        self.assertEqual(len("".join(n.addresses)), 568)

    def test_save_snapshot(self):
        t = self._set_receive()
        t.save_snapshot()
        s = t.snapshot_set.model.objects.first()
        self.assertEqual(s.data, t.json())
        self.assertEqual(s.topology, t)
        t.save_snapshot()
        s = t.snapshot_set.model.objects.first()
        self.assertFalse(s.created == s.modified)

    def test_label_addition(self):
        t = self._set_receive(parser='netdiff.OpenvpnParser')
        t.save()
        t.node_set.all().delete()
        data = self._load('static/openvpn.txt')
        t.receive(data)
        self.assertEqual(t.node_set.count(), 4)
        labels = []
        for node in t.node_set.all():
            labels.append(node.label)
        self.assertIn('Syskrack', labels)
        self.assertIn('Kali-Matera', labels)
        self.assertIn('pomezia', labels)

    def test_issue_58(self):
        self.node_model.objects.all().delete()
        self.link_model.objects.all().delete()
        t = self._set_receive()
        data = self._load('static/issue-58.json')
        t.receive(data)
        self.assertEqual(t.node_set.all().count(), 13)
        self.assertEqual(t.link_set.all().count(), 11)
