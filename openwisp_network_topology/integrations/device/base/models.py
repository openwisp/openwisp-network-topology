import logging
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string
from django.utils.timezone import datetime, now, timedelta
from django.utils.translation import gettext_lazy as _
from swapper import get_model_name, load_model

from openwisp_utils.base import UUIDModel

from .. import settings as app_settings

logger = logging.getLogger(__name__)

trigger_device_checks_path = "openwisp_monitoring.device.tasks.trigger_device_checks"


class AbstractDeviceNode(UUIDModel):
    node = models.OneToOneField(
        get_model_name("topology", "Node"), on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        get_model_name("config", "Device"), on_delete=models.CASCADE
    )

    # relations will be auto-created only for these parsers
    ENABLED_PARSERS = {
        "netdiff.OpenvpnParser": {
            "auto_create": "auto_create_openvpn",
            "link_down": "link_down_openvpn",
            "link_up": "link_up_openvpn",
        },
        "netdiff.WireguardParser": {
            "auto_create": "auto_create_wireguard",
        },
        "netdiff.ZeroTierParser": {
            "auto_create": "auto_create_zerotier",
        },
        "netdiff.NetJsonParser": {
            "auto_create": "auto_create_netjsongraph",
        },
    }

    class Meta:
        abstract = True
        unique_together = ("node", "device")

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
                node.save(update_fields=["organization_id"])
        except Exception:
            logger.exception("Exception raised during save_device_node")
            return
        else:
            logger.info(f"DeviceNode relation created for {node.label} - {device.name}")
            return device_node

    @classmethod
    def auto_create(cls, node):
        """
        Attempts to perform automatic creation of DeviceNode objects.
        The right action to perform depends on the Topology used.
        """
        opts = cls.ENABLED_PARSERS.get(node.topology.parser)
        if opts:
            return getattr(cls, opts["auto_create"])(node)

    @classmethod
    def auto_create_openvpn(cls, node):
        """
        Implementation of the integration between
        controller and network-topology modules
        when using OpenVPN (using the common name)
        """
        common_name = node.properties.get("common_name")
        if not common_name:
            return

        Device = load_model("config", "Device")
        device_filter = models.Q(config__vpnclient__cert__common_name=common_name)
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                "id", "name", "last_ip", "management_ip", "organization_id"
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return

        return cls.save_device_node(device, node)

    @classmethod
    def auto_create_wireguard(cls, node):
        allowed_ips = node.properties.get("allowed_ips")
        if not allowed_ips:
            return
        Device = load_model("config", "Device")
        ip_addresses = []
        for ip in allowed_ips:
            try:
                ip_addresses.extend([str(host) for host in ip_network(ip).hosts()])
            except ValueError:
                # invalid IP address
                continue
        device_filter = models.Q(config__vpnclient__ip__ip_address__in=ip_addresses)
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                "id", "name", "last_ip", "management_ip", "organization_id"
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return
        return cls.save_device_node(device, node)

    @classmethod
    def auto_create_zerotier(cls, node):
        """
        Implementation of the integration between
        controller and network-topology modules
        when using ZeroTier (using the `zerotier_member_id`)
        """
        zerotier_member_id = node.properties.get("address")
        if not zerotier_member_id:
            return

        Device = load_model("config", "Device")
        device_filter = models.Q(
            config__vpnclient__secret__startswith=zerotier_member_id
        )
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                "id", "name", "last_ip", "management_ip", "organization_id"
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
            # The first MAC address is Device.mac_address and
            # the second one is interface's MAC address.
            # If a node only has one MAC address, it means that
            # it only contains interface MAC address.
            return
        Device = load_model("config", "Device")
        device_filter = models.Q(
            mac_address__iexact=node.addresses[0].rpartition("@")[0]
        )
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                "id", "name", "last_ip", "management_ip", "organization_id"
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
            key = f"link_{status}"
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
            addresses = ", ".join(addresses)
            logger.warning(
                f"{e.__class__.__name__} raised while processing addresses: {addresses}"
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
        ).select_related("device", "node")

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
            if "openwisp_monitoring.device" in settings.INSTALLED_APPS:
                run_checks = import_string(trigger_device_checks_path)
                run_checks.delay(device_node.device.pk, recovery=link.status == "up")


class AbstractWifiMesh(UUIDModel):
    _NODE_PROPERTIES = [
        "ht",
        "vht",
        "he",
        "mfp",
        "wmm",
        "vendor",
    ]
    _LINK_PROPERTIES = [
        "auth",
        "authorized",
        "noise",
        "signal",
        "signal_avg",
        "mesh_llid",
        "mesh_plid",
        "mesh_plink",
        "mesh_non_peer_ps",
    ]

    topology = models.ForeignKey(
        get_model_name("topology", "Topology"), on_delete=models.CASCADE
    )
    mesh_id = models.CharField(
        max_length=32, null=False, blank=False, verbose_name=_("Mesh ID")
    )

    class Meta:
        abstract = True

    @classmethod
    def create_topology(cls, organization_ids, discard_older_data_time):
        if not app_settings.WIFI_MESH_INTEGRATION:
            raise ImproperlyConfigured(
                '"OPENIWSP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION" is set to "False".'
            )
        Link = load_model("topology", "Link")
        for org_id in organization_ids:
            intermediate_topologies = cls._create_intermediate_topologies(
                org_id, discard_older_data_time
            )
            if not intermediate_topologies:
                Link.objects.filter(
                    topology__wifimesh__isnull=False, organization_id=org_id
                ).exclude(topology__wifimesh__in=intermediate_topologies.keys()).update(
                    status="down"
                )
                continue
            cls._create_topology(intermediate_topologies, org_id)

    @classmethod
    def _create_intermediate_topologies(cls, organization_id, discard_older_data_time):
        """
        Creates an intermediate data structure for creating topologies.
        The intermediate topology contains intermediate data structure
        for nodes and links.

        Every device in the mesh sends monitoring data. The data contains
        information of the clients the device is connected to.
        Using the information sent by individual device, a hub-spoke
        topology is created between device (hub) and clients (spoke).
        These individual topologies are then complied to create the
        complete mesh topology.
        """
        DeviceData = load_model("device_monitoring", "DeviceData")
        intermediate_topologies = {}
        query = DeviceData.objects.filter(organization_id=organization_id).only(
            "mac_address"
        )
        discard_older_data_time = now() - timedelta(seconds=discard_older_data_time)
        for device_data in query.iterator():
            try:
                assert device_data.data is not None
                data_timestamp = datetime.fromisoformat(device_data.data_timestamp)
                assert data_timestamp > discard_older_data_time
            except (AttributeError, AssertionError):
                continue
            for interface in device_data.data.get("interfaces", []):
                if not AbstractWifiMesh._is_mesh_interfaces(interface):
                    continue
                mesh_id = "{}@{}".format(
                    interface["wireless"]["ssid"], interface["wireless"]["channel"]
                )
                if mesh_id not in intermediate_topologies:
                    intermediate_topologies[mesh_id] = {
                        "nodes": {},
                        "links": {},
                        "mac_mapping": {},
                    }
                topology = intermediate_topologies[mesh_id]
                (
                    collected_nodes,
                    collected_links,
                ) = cls._get_intermediate_nodes_and_links(
                    interface, device_data, topology["mac_mapping"]
                )
                AbstractWifiMesh._merge_nodes(
                    interface, topology["nodes"], collected_nodes
                )
                AbstractWifiMesh._merge_links(
                    interface, topology["links"], collected_links
                )
        return intermediate_topologies

    @classmethod
    def _get_intermediate_nodes_and_links(cls, interface, device_data, mac_mapping):
        """
        Create intermediate data structures for nodes and links.
        These intermediate data structures are required because the
        interface's MAC address can be different from the device's main
        MAC address. Thus, these data structures are aimed to provide
        quick lookup while mapping interface MAC address to the
        device MAC address.
        """
        device_mac = device_data.mac_address.upper()
        interface_mac = interface["mac"].upper()
        channel = interface["wireless"]["channel"]
        device_node_id = f"{device_mac}@{channel}"
        mac_mapping[interface_mac] = device_node_id
        collected_nodes = {}
        collected_links = {}
        for client in interface["wireless"].get("clients", []):
            client_mac = client["mac"].upper()
            node_properties = {}
            for property in cls._NODE_PROPERTIES:
                if property in client:
                    node_properties[property] = client[property]
            collected_nodes[client_mac] = {"properties": node_properties}
            if client.get("mesh_plink") and client.get("mesh_plink") != "ESTAB":
                # The link is not established.
                # Do not add this link to the topology.
                continue
            link_properties = {}
            for property in cls._LINK_PROPERTIES:
                if property in client:
                    link_properties[property] = client[property]

            collected_links[client_mac] = {
                interface_mac: {
                    "source": f"{device_mac}@{channel}",
                    "target": f"{client_mac}",
                    "cost": 1.0,
                    "properties": link_properties,
                }
            }
        return collected_nodes, collected_links

    @staticmethod
    def _is_mesh_interfaces(interface):
        return interface.get("wireless", False) and interface["wireless"].get(
            "mode"
        ) in ["802.11s"]

    @staticmethod
    def _merge_nodes(interface, topology_nodes, collected_nodes):
        interface_mac = interface["mac"].upper()
        topology_nodes.update(collected_nodes)
        if not topology_nodes.get(interface_mac):
            # Handle case when there is only one node present
            # in the mesh
            topology_nodes[interface_mac] = {}

    @staticmethod
    def _merge_links(interface, topology_links, collected_links):
        """
        Merges properties of links from the topology stored
        in the database (topology_links) with link collected from
        the interface's wireless client data (collected_links).

        It takes into consideration the nature of the property
        (e.g. taking average for signal and noise, etc.).
        """
        interface_mac = interface["mac"].upper()
        if topology_links.get(interface_mac):
            for source, topology_link in topology_links[interface_mac].items():
                if not collected_links.get(source):
                    continue
                for property, value in collected_links[source][interface_mac][
                    "properties"
                ].items():
                    if isinstance(value, int):
                        # If the value is integer, then take average of the
                        # values provided by the two nodes.
                        # This is for fields like signal and noise.
                        if topology_link["properties"].get(property):
                            topology_link["properties"][property] = (
                                value + topology_link["properties"][property]
                            ) // 2
                        else:
                            # The link in topology does not contain this property,
                            # hence instead of averaging, assign the current value.
                            topology_link["properties"][property] = value
                    elif (
                        property in ["mesh_plink", "mesh_non_peer_ps"]
                        and topology_link["properties"].get(property)
                        and value != topology_link["properties"][property]
                    ):
                        # The value for "mesh_plink" and "mesh_non_peer_ps" properties
                        # should be reported same by both the nodes.
                        # Flag the value as inconsistent if they are different.
                        topology_link["properties"][property] = (
                            "INCONSISTENT: ({} / {})".format(
                                value,
                                topology_link["properties"][property],
                            )
                        )
                collected_links.pop(source)
        for key, value in collected_links.items():
            try:
                topology_links[key].update(value)
            except KeyError:
                topology_links[key] = value

    @staticmethod
    def _create_topology(intermediate_topologies, organization_id):
        for mesh_id, intermediate in intermediate_topologies.items():
            topology_obj = AbstractWifiMesh._get_mesh_topology(mesh_id, organization_id)
            nodes = AbstractWifiMesh._get_nodes_from_intermediate_topology(intermediate)
            links = AbstractWifiMesh._get_links_from_intermediate_topology(intermediate)
            topology = {
                "type": "NetworkGraph",
                "protocol": "Mesh",
                "version": "1",
                "metric": "Airtime",
                "nodes": nodes,
                "links": links,
            }
            topology_obj.receive(topology)

    @staticmethod
    def _get_nodes_from_intermediate_topology(intermediate_topology):
        """
        Using the "intermediate_topology", return all the
        nodes of the topology.

        It maps the interface's MAC address to the device's main MAC address
        which is used to create DeviceNode relation.
        """
        nodes = []
        mac_mapping = intermediate_topology["mac_mapping"]
        for interface_mac, intermediate_node in intermediate_topology["nodes"].items():
            device_mac = mac_mapping.get(interface_mac)
            if not device_mac:
                continue
            node = {
                "id": device_mac,
                "label": device_mac,
                "local_addresses": [interface_mac],
            }
            if intermediate_node.get("properties"):
                node["properties"] = intermediate_node["properties"]
            nodes.append(node)
        return nodes

    @staticmethod
    def _get_links_from_intermediate_topology(intermediate_topology):
        """
        Using the "intermediate_topology", return all the
        links of the topology.

        It maps the interface's MAC address to the device's main MAC address.
        """
        links = []
        mac_mapping = intermediate_topology["mac_mapping"]
        for interface_mac, intermediate_link in intermediate_topology["links"].items():
            device_mac = mac_mapping.get(interface_mac)
            if not device_mac:
                continue
            for link in intermediate_link.values():
                link["target"] = device_mac
                links.append(link)
        return links

    @staticmethod
    def _get_mesh_topology(mesh_id, organization_id):
        """
        Get or create topology for the given mesh_id and organization_id.
        It also creates WifiMesh object to keep track of mesh's ID
        if a new topology object is created.
        """
        Topology = load_model("topology", "Topology")
        WifiMesh = load_model("topology_device", "WifiMesh")
        try:
            mesh_topology = (
                WifiMesh.objects.select_related("topology")
                .get(
                    mesh_id=mesh_id,
                    topology__organization_id=organization_id,
                )
                .topology
            )
        except WifiMesh.DoesNotExist:
            mesh_topology = Topology(
                organization_id=organization_id,
                label=mesh_id,
                parser="netdiff.NetJsonParser",
                strategy="receive",
                expiration_time=330,
            )
            mesh_topology.full_clean()
            mesh_topology.save()
            wifi_mesh = WifiMesh(
                mesh_id=mesh_id,
                topology=mesh_topology,
            )
            wifi_mesh.full_clean()
            wifi_mesh.save()
        return mesh_topology
