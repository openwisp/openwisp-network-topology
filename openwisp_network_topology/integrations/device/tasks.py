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
    WifiMesh = swapper.load_model('topology_device', 'WifiMesh')
    Device = swapper.load_model('config', 'Device')
    try:
        device = Device.objects.only('id', 'mac_address', 'organization_id').get(
            id=device_id
        )
    except Device.DoesNotExist:
        return
    WifiMesh.create_topology(interface, device)
