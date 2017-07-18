from django_netjsongraph.management.commands import BaseUpdateCommand

from openwisp_network_topology.models import Topology


class Command(BaseUpdateCommand):
    topology_model = Topology
