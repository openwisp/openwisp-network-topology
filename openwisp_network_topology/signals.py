from asgiref.sync import async_to_sync
from channels import layers
from django.dispatch import Signal

update_topology = Signal()
update_topology.__doc__ = """
Providing arguments: ['topology']
"""


def broadcast_topology(topology, *args, **kwargs):
    channel_layer = layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"topology-{topology.pk}",
        {"type": "send_topology_update", "data": topology.json()},
    )
