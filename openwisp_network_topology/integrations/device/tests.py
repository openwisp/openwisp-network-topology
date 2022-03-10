from unittest import mock

import swapper
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import transaction
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils.module_loading import import_string
from openwisp_controller.config.tests.utils import (
    CreateConfigTemplateMixin,
    TestVpnX509Mixin,
)

from openwisp_network_topology.tests.utils import CreateGraphObjectsMixin
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.admin_theme.dashboard import DASHBOARD_CHARTS, DASHBOARD_TEMPLATES
from openwisp_utils.admin_theme.menu import MENU

from .base.models import logger as models_logger
from .base.models import trigger_device_checks_path

Node = swapper.load_model('topology', 'Node')
Link = swapper.load_model('topology', 'Link')
Topology = swapper.load_model('topology', 'Topology')
DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
Device = swapper.load_model('config', 'Device')
Template = swapper.load_model('config', 'Template')
Vpn = swapper.load_model('config', 'Template')
Organization = swapper.load_model('openwisp_users', 'Organization')
Cert = swapper.load_model('pki', 'Cert')


class Base(
    TestVpnX509Mixin,
    CreateConfigTemplateMixin,
    CreateGraphObjectsMixin,
    TestOrganizationMixin,
):
    topology_model = Topology
    node_model = Node

    def _init_test_node(
        self,
        topology,
        addresses=None,
        label='test',
        common_name=None,
        create=True,
    ):
        if not addresses:
            addresses = ['netjson_id']
        node = Node(
            organization=topology.organization,
            topology=topology,
            label=label,
            addresses=addresses,
            properties={'common_name': common_name},
        )
        if create:
            node.full_clean()
            node.save()
        return node

    def _create_test_env(self, parser):
        organization = self._get_org()
        vpn = self._create_vpn(name='test VPN', organization=organization)
        self._create_template(
            name='VPN',
            type='vpn',
            vpn=vpn,
            config=vpn.auto_client(),
            default=True,
            organization=organization,
        )
        vpn2 = self._create_vpn(name='test VPN2', ca=vpn.ca, organization=organization)
        self._create_template(
            name='VPN2',
            type='vpn',
            vpn=vpn2,
            config=vpn.auto_client(),
            default=True,
            organization=organization,
        )
        device = self._create_device(organization=organization)
        config = self._create_config(device=device)
        topology = self._create_topology(organization=organization, parser=parser)
        cert = config.vpnclient_set.first().cert
        return topology, device, cert


class TestControllerIntegration(Base, TransactionTestCase):
    def test_auto_create_openvpn(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        self.assertEqual(DeviceNode.objects.count(), 0)
        with self.subTest('assert number of queries'):
            with self.assertNumQueries(13):
                node = self._init_test_node(topology, common_name=cert.common_name)
        self.assertEqual(DeviceNode.objects.count(), 1)
        device_node = DeviceNode.objects.first()
        self.assertEqual(device_node.device, device)
        self.assertEqual(device_node.node, node)

        with self.subTest('not run on save'):
            with mock.patch.object(transaction, 'on_commit') as on_commit:
                node.save()
                on_commit.assert_not_called()

    def test_auto_create_openvpn_failures(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')

        with self.subTest('common_name not present'):
            self._init_test_node(topology)
            self.assertFalse(DeviceNode.objects.exists())

        with self.subTest('cert does not exist'):
            self._init_test_node(topology, common_name='missing')
            self.assertFalse(DeviceNode.objects.exists())

        with self.subTest('exception during save'):
            with mock.patch.object(
                DeviceNode, 'save', side_effect=Exception('test')
            ) as save:
                with mock.patch.object(models_logger, 'exception') as logger_exception:
                    self._init_test_node(topology, common_name=cert.common_name)
                    save.assert_called_once()
                    logger_exception.assert_called_once()
                    self.assertEqual(DeviceNode.objects.count(), 0)

    def test_filter_by_link(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')

        with self.subTest('empty result'):
            node = self._init_test_node(topology, common_name=cert.common_name)
            self.assertFalse(DeviceNode.filter_by_link(Link()).exists())

        with self.subTest('non empty result'):
            node2 = self._init_test_node(
                topology, addresses=['netjson_id2'], label='test2'
            )
            link = Link(
                source=node,
                target=node2,
                topology=topology,
                organization=topology.organization,
                cost=1,
            )
            link.full_clean()
            link.save()
            self.assertTrue(DeviceNode.filter_by_link(link).exists())

    def test_link_down_openvpn(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node = self._init_test_node(topology, common_name=cert.common_name)
        node2 = self._init_test_node(topology, addresses=['netjson_id2'], label='test2')
        device.management_ip = '10.0.0.8'
        device.save()
        link = Link(
            source=node,
            target=node2,
            status='up',
            topology=topology,
            organization=topology.organization,
            cost=1,
        )
        link.full_clean()
        link.save()
        with self.assertNumQueries(4):
            link.status = 'down'
            link.save()
        device.refresh_from_db()
        self.assertIsNone(device.management_ip)

    def test_link_up_openvpn(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node = self._init_test_node(
            topology, addresses=['netjson_id', '10.0.0.2'], common_name=cert.common_name
        )
        node2 = self._init_test_node(topology, addresses=['netjson_id2'], label='test2')
        device.management_ip = None
        device.save()
        link = Link(
            source=node,
            target=node2,
            status='down',
            topology=topology,
            organization=topology.organization,
            cost=1,
        )
        link.full_clean()
        link.save()
        with self.assertNumQueries(4):
            link.status = 'up'
            link.save()
        device.refresh_from_db()
        self.assertEqual(device.management_ip, '10.0.0.2')

    @mock.patch.object(models_logger, 'warning')
    def test_link_up_openvpn_failure(self, logger_warning):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node = self._init_test_node(
            topology,
            addresses=['netjson_id', 'not_an_ip'],
            common_name=cert.common_name,
        )
        node2 = self._init_test_node(topology, addresses=['netjson_id2'], label='test2')
        device.management_ip = None
        device.save()
        link = Link(
            source=node,
            target=node2,
            status='down',
            topology=topology,
            organization=topology.organization,
            cost=1,
        )
        link.full_clean()
        link.save()

        with self.subTest('Test invalid addresses'):
            link.status = 'up'
            link.save()
            logger_warning.assert_called_once()
            logger_warning.assert_called_with(
                'ValueError raised while processing addresses: netjson_id, not_an_ip'
            )

        link.status = 'down'
        link.save()
        logger_warning.reset_mock()

        with self.subTest('Test disconnected nodes'):
            node.addresses = ['10.0.0.1']
            node.save()
            link.status = 'up'
            link.save()
            logger_warning.assert_called_once()
            logger_warning.assert_called_with(
                'IndexError raised while processing addresses: 10.0.0.1'
            )

        device.refresh_from_db()
        self.assertIsNone(device.management_ip)

    def test_node_label_override(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node = self._init_test_node(topology, common_name=cert.common_name)
        node.refresh_from_db()
        self.assertEqual(node.get_name(), device.name)

    def test_topology_json(self):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        self._init_test_node(topology, common_name=cert.common_name)
        with self.subTest('assert number of queries'):
            with self.assertNumQueries(2):
                json = topology.json(dict=True)
        self.assertEqual(json['nodes'][0]['label'], device.name)

    def test_create_device_nodes_command(self):
        topology, _, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        properties = {'common_name': cert.common_name}
        n = self._create_node(topology=topology, properties=properties)
        DeviceNode.objects.all().delete()
        call_command('create_device_nodes')
        qs = DeviceNode.objects.filter(node=n)
        self.assertEqual(qs.count(), 1)

    def test_shared_topology_org_devices(self):
        org1 = self._create_org(name='org1')
        org2 = self._create_org(name='org2')
        shared_topology = self._create_topology(
            organization=None, parser='netdiff.OpenvpnParser'
        )
        shared_vpn = self._create_vpn(name='test VPN', organization=None)
        self._create_template(
            name='VPN',
            type='vpn',
            vpn=shared_vpn,
            config=shared_vpn.auto_client(),
            default=True,
            organization=None,
        )
        org1_device = self._create_device(organization=org1)
        self._create_config(device=org1_device)
        org1_cert_common_name = (
            org1_device.config.vpnclient_set.first().cert.common_name
        )
        org2_device = self._create_device(organization=org2)
        self._create_config(device=org2_device)
        org2_cert_common_name = (
            org2_device.config.vpnclient_set.first().cert.common_name
        )

        openvpn_status = (
            'OpenVPN CLIENT LIST\n'
            'Updated,Sun Oct  8 19:46:06 2017\n'
            'Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since\n'
            f'{org1_cert_common_name},87.7.9.213:56857,417209,6046898,Sun Oct  8 08:39:11 2017\n'
            f'{org2_cert_common_name},2.226.154.66:52091,6020304,444463,Sun Oct  8 08:39:10 2017\n'
            'ROUTING TABLE\n'
            'Virtual Address,Common Name,Real Address,Last Ref\n'
            f'9e:c2:f2:55:f4:33,{org1_cert_common_name},87.7.9.213:56857,Sun Oct  8 19:45:37 2017\n'
            f'46:8a:69:e7:46:24,{org2_cert_common_name},2.226.154.66:52091,Sun Oct  8 19:45:37 2017\n'
            'GLOBAL STATS\n'
            'Max bcast/mcast queue length,6\n'
            'END'
        )
        shared_topology.receive(openvpn_status)
        self.assertEqual(DeviceNode.objects.count(), 2)
        org1_node = DeviceNode.objects.get(device=org1_device).node
        org2_node = DeviceNode.objects.get(device=org2_device).node
        self.assertEqual(org1_node.organization, org1)
        self.assertEqual(org2_node.get_organization_id(), org2.id)


class TestMonitoringIntegration(Base, TransactionTestCase):
    @mock.patch('openwisp_monitoring.db.timeseries_db.create_database')
    @mock.patch('openwisp_monitoring.device.utils.manage_short_retention_policy')
    @mock.patch('openwisp_notifications.types.NOTIFICATION_TYPES', dict())
    def test_monitoring_integration(self, *args):
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node = self._init_test_node(
            topology, addresses=['netjson_id', '10.0.0.2'], common_name=cert.common_name
        )
        node2 = self._init_test_node(topology, addresses=['netjson_id2'], label='test2')
        device.management_ip = None
        device.save()
        link = Link(
            source=node,
            target=node2,
            status='up',
            topology=topology,
            organization=topology.organization,
            cost=1,
        )
        link.full_clean()
        link.save()
        DASHBOARD_CHARTS.clear()
        DASHBOARD_TEMPLATES.clear()
        MENU.clear()
        # needed for monitoring
        trigger_device_checks = import_string(trigger_device_checks_path)
        with mock.patch.object(trigger_device_checks, 'delay') as mocked_task:
            with self.modify_settings(
                INSTALLED_APPS={
                    'append': [
                        'openwisp_monitoring.monitoring',
                        'openwisp_monitoring.device',
                        'openwisp_monitoring.check',
                        'openwisp_controller.connection',
                        'openwisp_notifications',
                    ]
                }
            ):
                link.status = 'down'
                link.save()
            mocked_task.assert_called_once()
            mocked_task.assert_called_with(device.pk, recovery=False)


class TestAdmin(Base, TransactionTestCase):
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
        topology, device, cert = self._create_test_env(parser='netdiff.OpenvpnParser')
        node1 = self._init_test_node(topology, common_name=cert.common_name)
        node2 = self._init_test_node(topology, addresses=['netjson_id2'], label='test2')
        link = Link(
            source=node1,
            target=node2,
            topology=topology,
            organization=topology.organization,
            cost=1,
        )
        link.full_clean()
        link.save()
        self._create_link(topology=topology, source=node1, target=node2)
        self.client.force_login(self.user_model.objects.get(username='admin'))

    def test_node_change_list_queries(self):
        path = reverse('{0}_node_changelist'.format(self.prefix))
        with self.assertNumQueries(7):
            self.client.get(path)

    def test_link_change_list_queries(self):
        path = reverse('{0}_link_changelist'.format(self.prefix))
        with self.assertNumQueries(7):
            self.client.get(path)

    def test_link_node_different_topology(self):
        Topology.objects.all().delete()
        org = self._create_org()
        topology1 = self._create_topology(organization=org)
        topology2 = self._create_topology(organization=org)
        node1 = self._init_test_node(topology2)
        node2 = self._init_test_node(topology2)
        link = Link(
            source=node1,
            target=node2,
            topology=topology1,
            organization=topology1.organization,
            cost=1,
        )
        with self.assertRaises(ValidationError) as context:
            # Raises ValidationError if link belongs to diff topologies
            link.full_clean()
        self.assertIn('source', context.exception.error_dict)
        self.assertIn('target', context.exception.error_dict)
