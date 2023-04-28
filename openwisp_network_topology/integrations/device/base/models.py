import json
import logging
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.db import models, transaction
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from swapper import get_model_name, load_model

from openwisp_utils.base import UUIDModel

from ..tasks import create_mesh_topology

logger = logging.getLogger(__name__)

trigger_device_checks_path = 'openwisp_monitoring.device.tasks.trigger_device_checks'


class AbstractDeviceNode(UUIDModel):
    node = models.OneToOneField(
        get_model_name('topology', 'Node'), on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        get_model_name('config', 'Device'), on_delete=models.CASCADE
    )

    # relations will be auto-created only for these parsers
    ENABLED_PARSERS = {
        'netdiff.OpenvpnParser': {
            'auto_create': 'auto_create_openvpn',
            'link_down': 'link_down_openvpn',
            'link_up': 'link_up_openvpn',
        },
        'netdiff.WireguardParser': {
            'auto_create': 'auto_create_wireguard',
        },
        'netdiff.NetJsonParser': {
            'auto_create': 'auto_create_netjsongraph',
        },
    }

    class Meta:
        abstract = True
        unique_together = ('node', 'device')

    @classmethod
    def save_device_node(cls, device, node):
        device_node = cls(device=device, node=node)
        try:
            device_node.full_clean()
            device_node.save()
            # Update organization of the node. This is required
            # when topology is shared.
            if node.organization_id is None:
                node.organization_id = device.organization_id
                node.save(update_fields=['organization_id'])
        except Exception:
            logger.exception('Exception raised during save_device_node')
            return
        else:
            logger.info(f'DeviceNode relation created for {node.label} - {device.name}')
            return device_node

    @classmethod
    def auto_create(cls, node):
        """
        Attempts to perform automatic creation of DeviceNode objects.
        The right action to perform depends on the Topology used.
        """
        opts = cls.ENABLED_PARSERS.get(node.topology.parser)
        if opts:
            return getattr(cls, opts['auto_create'])(node)

    @classmethod
    def auto_create_openvpn(cls, node):
        """
        Implementation of the integration between
        controller and network-topology modules
        when using OpenVPN (using the common name)
        """
        common_name = node.properties.get('common_name')
        if not common_name:
            return

        Device = load_model('config', 'Device')
        device_filter = models.Q(config__vpnclient__cert__common_name=common_name)
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                'id', 'name', 'last_ip', 'management_ip', 'organization_id'
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return

        return cls.save_device_node(device, node)

    @classmethod
    def auto_create_wireguard(cls, node):
        allowed_ips = node.properties.get('allowed_ips')
        if not allowed_ips:
            return
        Device = load_model('config', 'Device')
        ip_addresses = []
        for ip in allowed_ips:
            try:
                network = ip_network(ip)
                if network.prefixlen == network._max_prefixlen:
                    # In python 3.7, hosts method is not returning any ip
                    # if subnet mask is 32, resolved in future python releases
                    # https://bugs.python.org/issue28577
                    ip_addresses.append(str(network.network_address))
                else:
                    ip_addresses.extend([str(host) for host in ip_network(ip).hosts()])
            except ValueError:
                # invalid IP address
                continue
        device_filter = models.Q(config__vpnclient__ip__ip_address__in=ip_addresses)
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                'id', 'name', 'last_ip', 'management_ip', 'organization_id'
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return
        return cls.save_device_node(device, node)

    @classmethod
    def auto_create_netjsongraph(cls, node):
        if len(node.addresses) < 2:
            # The second MAC address in node.addresses is same as
            # Device.mac_address. Therefore, it is used for lookup.
            return
        Device = load_model('config', 'Device')
        device_filter = models.Q(mac_address__iexact=node.addresses[-1])
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                'id', 'name', 'last_ip', 'management_ip', 'organization_id'
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return
        return cls.save_device_node(device, node)

    def link_action(self, link, status):
        """
        Performs clean-up operations when link goes down.
        The right action to perform depends on the Topology used.
        """
        opts = self.ENABLED_PARSERS.get(link.topology.parser)
        if opts:
            key = f'link_{status}'
            if key in opts and hasattr(self, opts[key]):
                return getattr(self, opts[key])()

    def link_down_openvpn(self):
        """
        Link down action for OpenVPN
        """
        self.device.management_ip = None
        self.device.save()

    def link_up_openvpn(self):
        """
        Link up action for OpenVPN
        """
        addresses = self.node.addresses
        try:
            address = ip_address(addresses[1])
        except (IndexError, ValueError) as e:
            addresses = ', '.join(addresses)
            logger.warning(
                f'{e.__class__.__name__} raised while processing addresses: {addresses}'
            )
        else:
            self.device.management_ip = str(address)
            self.device.save()

    @classmethod
    def filter_by_link(cls, link):
        """
        Returns a queryset which looks for a DeviceNode which is related
        to the specified Link instance.
        """
        return cls.objects.filter(
            models.Q(node__source_link_set__pk=link.pk)
            | models.Q(node__target_link_set__pk=link.pk)
        ).select_related('device', 'node')

    @classmethod
    def trigger_device_updates(cls, link):
        """
        Used to refresh controller and monitoring information
        whenever the status of a link changes
        """
        if link.topology.parser not in cls.ENABLED_PARSERS:
            return
        for device_node in cls.filter_by_link(link):
            device_node.link_action(link, link.status)
            # triggers monitoring checks if OpenWISP Monitoring is enabled
            if 'openwisp_monitoring.device' in settings.INSTALLED_APPS:
                run_checks = import_string(trigger_device_checks_path)
                run_checks.delay(device_node.device.pk, recovery=link.status == 'up')


class AbstractWifiMesh(UUIDModel):
    topology = models.ForeignKey(
        get_model_name('topology', 'Topology'), on_delete=models.CASCADE
    )
    ssid = models.CharField(
        max_length=32, null=False, blank=False, verbose_name=_('Mesh SSID')
    )

    class Meta:
        abstract = True

    @classmethod
    def create_wifi_mesh_topology_receiver(cls, instance, *args, **kwargs):
        """
        It iterates through the interfaces of the device reported
        by openwisp-monitoring and asynchronously creates topology
        for mesh interfaces.
        """
        for interface in instance.data.get('interfaces', []):
            if not interface.get('wireless'):
                continue
            if not interface['wireless'].get('mode') in ['802.11s']:
                continue
            # This is a mesh interface. Get topology for this mesh.
            create_mesh_topology.delay(interface, instance.id)

    @classmethod
    def create_topology(cls, interface, device):
        mesh_topology = cls._get_mesh_topology(interface, device)
        graph = cls._create_netjsongraph(interface, device)
        create_device_node = cls._update_graph_from_db(graph, mesh_topology, interface)
        mesh_topology.receive(json.dumps(graph))
        if create_device_node:
            transaction.on_commit(
                lambda: cls._create_device_node(device, mesh_topology)
            )

    @staticmethod
    def _get_mesh_topology(interface, device):
        """
        Get or create topology for the given interface and device.
        It also creates WifiMesh object to keep track of mesh's SSID
        if a new topology object is created.
        """
        Topology = load_model('topology', 'Topology')
        WifiMesh = load_model('topology_device', 'WifiMesh')

        try:
            mesh_topology = (
                WifiMesh.objects.select_related('topology')
                .get(
                    ssid=interface['wireless']['ssid'],
                    topology__organization_id=device.organization_id,
                )
                .topology
            )
        except WifiMesh.DoesNotExist:
            mesh_topology = Topology(
                organization_id=device.organization_id,
                label=interface['wireless']['ssid'],
                parser='netdiff.NetJsonParser',
                strategy='receive',
                expiration_time=330,
            )
            mesh_topology.full_clean()
            mesh_topology.save()
            wifi_mesh = WifiMesh(
                ssid=interface['wireless']['ssid'], topology=mesh_topology
            )
            wifi_mesh.full_clean()
            wifi_mesh.save()
        return mesh_topology

    @staticmethod
    def _create_netjsongraph(interface, device):
        """
        Creates a topology graph (dict) that resembles NetJSONGraph structure
        using the wireless client data present in interface.

        Note: The "node" and "links" keys of the returned graph
        does not follow NetJSON specification.
        """
        NODE_PROPERTIES = [
            'ht',
            'vht',
            'he',
            'mfp',
            'wmm',
            'vendor',
            'mesh_llid',
            'mesh_plid',
            'mesh_plink',
            'mesh_non_peer_ps',
        ]
        LINK_PROPERTIES = ['auth', 'authorized', 'noise', 'signal', 'signal_avg']
        interface_mac = interface['mac'].upper()
        collected_nodes = {
            interface_mac: {
                'id': interface_mac,
                'label': interface_mac,
                'local_addresses': [device.mac_address.upper()],
                'properties': {},
            }
        }
        collected_links = {}
        for client in interface['wireless'].get('clients', []):
            client_mac = client['mac'].upper()
            collected_nodes[client_mac] = {
                'id': client_mac,
                'label': client_mac,
                'properties': {},
            }
            for property in NODE_PROPERTIES:
                if property in client:
                    collected_nodes[client_mac]['properties'][property] = client.get(
                        property
                    )

            collected_links[client_mac] = {
                'source': interface_mac,
                'target': client_mac,
                'cost': 1.0,
                'properties': {},
            }
            for property in LINK_PROPERTIES:
                if property in client:
                    collected_links[client_mac]['properties'][property] = client.get(
                        property
                    )

        return {
            'type': 'NetworkGraph',
            'protocol': 'Mesh',
            'version': '1',
            'metric': 'Airtime',
            'nodes': collected_nodes,
            'links': collected_links,
        }

    @staticmethod
    def _update_graph_from_db(graph, mesh_topology, interface):
        """
        Merges the data of "nodes" and "links" of the graph
        with existing data from DB.

        This prevents losing data from the topology due
        to overwrites.
        """

        def _merge_link_data(collected_link, db_link):
            for key, value in db_link.properties.items():
                if key not in collected_link['properties']:
                    collected_link['properties'][key] = value
                elif isinstance(value, int):
                    collected_link['properties'][key] = (
                        collected_link['properties'][key] + value
                    ) // 2

        def _merge_node_data(collected_node, db_node):
            create_device_node = True
            if 'local_addresses' in collected_node:
                # Only the collected node for the current device
                # contains "local_address"
                if db_node.local_addresses:
                    # The node for the current device already contains
                    # MAC address of the device. This signifies a DeviceNode
                    # has already been created for the device.
                    create_device_node = False
            elif db_node.local_addresses:
                # Collected nodes for other devices does not contain "local_addresses".
                # Update the "local_addresses" for these nodes from the database,
                # this prevents deleting this information from the database.
                collected_node['local_addresses'] = db_node.local_addresses
            for key, value in db_node.properties.items():
                if key not in collected_node['properties']:
                    collected_node['properties'][key] = value
            return create_device_node

        Link = load_model('topology', 'Link')

        create_device_node = True
        collected_nodes = graph.pop('nodes')
        collected_links = graph.pop('links')
        device_mac_address = interface['mac'].upper()
        current_device_node = None
        where = models.Q(source__topology_id=mesh_topology.id) & (
            (
                models.Q(source__label=device_mac_address)
                & models.Q(target__label__in=collected_nodes.keys())
            )
            | (
                models.Q(target__label=device_mac_address)
                & models.Q(source__label__in=collected_nodes.keys())
            )
        )
        for link in (
            Link.objects.select_related('source', 'target').filter(where).iterator()
        ):
            if link.source.label == device_mac_address:
                _merge_link_data(collected_links[link.target.label], link)
                _merge_node_data(collected_nodes[link.target.label], link.target)
                current_device_node = link.source
            else:
                _merge_link_data(collected_links[link.source.label], link)
                _merge_node_data(collected_nodes[link.source.label], link.source)
                current_device_node = link.target
        if current_device_node:
            create_device_node &= _merge_node_data(
                collected_nodes[current_device_node.label], current_device_node
            )
        graph['nodes'] = list(collected_nodes.values())
        graph['links'] = list(collected_links.values())
        return create_device_node

    @staticmethod
    def _create_device_node(device, mesh_topology):
        Node = load_model('topology', 'Node')
        DeviceNode = load_model('topology_device', 'DeviceNode')
        node = Node.objects.select_related('devicenode').get(
            organization_id=device.organization_id,
            addresses__icontains=device.mac_address.upper(),
            topology_id=mesh_topology.id,
        )
        DeviceNode.auto_create(node)
