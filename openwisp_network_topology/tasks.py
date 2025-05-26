import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from swapper import load_model

logger = logging.getLogger(__name__)


@shared_task
def handle_update_topology(topology_pk, diff):
    """
    A Celery task that updates the network topology
    of a Topology instance in the background.

    Args:
        topology_pk (uuid):
        The primary key of the Topology instance.

        diff (str):
        A dict containing the network topology diff.
    """
    Topology = load_model("topology", "Topology")
    try:
        topology = Topology.objects.get(pk=topology_pk)
    except ObjectDoesNotExist as e:
        logger.warning(f'handle_update_topology("{topology_pk}") failed: {e}')
        return
    topology.update_topology(diff)
