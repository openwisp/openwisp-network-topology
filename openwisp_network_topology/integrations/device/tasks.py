import json

import swapper
from celery import shared_task


@shared_task
def create_device_node_relation(node_pk):
    Node = swapper.load_model('topology', 'Node')
    DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
    node = Node.objects.select_related('topology').get(pk=node_pk)
    DeviceNode.auto_create(node)


@shared_task
def trigger_device_updates(link_pk):
    Link = swapper.load_model('topology', 'Link')
    DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
    link = Link.objects.select_related('topology').get(pk=link_pk)
    DeviceNode.trigger_device_updates(link)


@shared_task
def create_mesh_topology(interface, device_id):
    Topology = swapper.load_model('topology', 'Topology')
    Node = swapper.load_model('topology', 'Node')
    DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
    WifiMesh = swapper.load_model('topology_device', 'WifiMesh')
    Device = swapper.load_model('config', 'Device')
    create_device_node = True
    try:
        device = Device.objects.only('id', 'organization_id').get(id=device_id)
    except Device.DoesNotExist:
        return
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
            organization=device.organization,
            label=interface['wireless']['ssid'],
            parser='netdiff.NetJsonParser',
            strategy='receive',
            expiration_time=330,
        )
        mesh_topology.full_clean()
        mesh_topology.save()
        wifi_mesh = WifiMesh(ssid=interface['wireless']['ssid'], topology=mesh_topology)
        wifi_mesh.full_clean()
        wifi_mesh.save()

    # Create NetJSONGraph for this mesh
    interface_mac = interface['mac'].upper()
    graph = {
        'type': 'NetworkGraph',
        'protocol': 'OLSR',
        'version': '1',
        'metric': 'ETX',
        'nodes': [
            {
                'id': interface_mac,
                'label': interface_mac,
                'local_addresses': [device.mac_address.upper()],
            }
        ],
        'links': [],
    }
    collected_nodes = {
        interface_mac: {
            'id': interface_mac,
            'label': interface_mac,
            'local_addresses': [device.mac_address.upper()],
        }
    }
    for client in interface['wireless']['clients']:
        client_mac = client['mac'].upper()
        collected_nodes[client_mac] = {'id': client_mac, 'label': client_mac}
        graph['links'].append(
            {
                'source': interface_mac,
                'target': client_mac,
                'cost': 1.0,
            }
        )
    for node in Node.objects.only('properties', 'addresses').filter(
        topology_id=mesh_topology.id, label__in=collected_nodes.keys()
    ):
        if 'local_address' in collected_nodes[node.label]:
            # Only the collected node for the current device
            # contains "local_address"
            if node.local_addresses:
                # The node for the current device already contains
                # MAC address of the device. This signifies a DeviceNode
                # has already been created for the device.
                create_device_node = False
        elif node.local_addresses:
            # Collected nodes for other devices does not contain "local_addresses".
            # Updated the "local_addresses" for these nodes from the database,
            # this prevents deleting this information from the database.
            collected_nodes[node.label]['local_addresses'] = node.local_addresses

    graph['nodes'] = list(collected_nodes.values())
    mesh_topology.receive(json.dumps(graph))

    if not create_device_node:
        return
    try:
        node = Node.objects.select_related('devicenode').get(
            organization_id=device.organization_id,
            addresses__icontains=interface_mac,
            topology_id=mesh_topology.id,
        )
    except Node.DoesNotExist:
        # The node for this device does not exist.
        # The DeviceNode will be created when node for this
        # device is created.
        pass
    else:
        if not hasattr(node, 'devicenode'):
            DeviceNode.auto_create(node)
