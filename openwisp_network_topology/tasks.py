import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from swapper import load_model

logger = logging.getLogger(__name__)


@shared_task
def handle_topology_receive(topology_pk, data):
    """
    A Celery task that receives topology data
    from ReceiveTopologyView and perform topology.receive(data)

    Args:
        topology_pk (str):
        The primary key of the Topology instance.

        data (str):
        A dict containing the topology data
        to be written to the database.
    """
    Topology = load_model('topology', 'Topology')
    try:
        topology = Topology.objects.get(pk=topology_pk)
    except ObjectDoesNotExist as e:
        logger.warning(f'handle_topology_receive("{topology_pk}") failed: {e}')
        return
    topology.receive(data)
