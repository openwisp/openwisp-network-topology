import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from swapper import load_model

from .utils import is_write_blocked

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
        topology = Topology.objects.select_related("organization").get(pk=topology_pk)
    except ObjectDoesNotExist as e:
        logger.warning(f'handle_update_topology("{topology_pk}") failed: {e}')
        return
    if is_write_blocked(topology):
        logger.info(
            "Skipped handle_update_topology for topology %s: organization disabled",
            topology_pk,
        )
        return
    topology.update_topology(diff)


@shared_task
def handle_disabled_organization(organization_id):
    """
    A Celery task that marks the links of a disabled
    organization's topologies as down.
    """
    Link = load_model("topology", "Link")
    Link.mark_organization_links_down(organization_id)
