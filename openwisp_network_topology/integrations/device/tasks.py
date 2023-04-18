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
    graph = {
        'type': 'NetworkGraph',
        'protocol': 'OLSR',
        'version': '1',
        'metric': 'ETX',
        'nodes': [
            {
                'id': interface['mac'],
                'label': interface['mac'],
                'properties': {
                    'device_id': str(device.id),
                },
            }
        ],
        'links': [],
    }
    for client in interface['wireless']['clients']:
        graph['nodes'].append({'id': client['mac'], 'label': client['mac']})
        graph['links'].append(
            {
                'source': interface['mac'],
                'target': client['mac'],
                'cost': 1.0,
            }
        )
    try:
        node = Node.objects.get(
            organization_id=device.organization_id,
            addresses__icontains=interface['mac'],
            topology_id=mesh_topology.id,
        )
    except Node.DoesNotExist:
        # The node for this device does not exist.
        # The DeviceNode will be created when node for this
        # device is created.
        pass
    else:
        if not DeviceNode.objects.filter(device_id=device.id, node_id=node.id).exists():
            device_node = DeviceNode(device_id=device.id, node_id=node.id)
            device_node.full_clean()
            device_node.save()
    mesh_topology.receive(json.dumps(graph))
