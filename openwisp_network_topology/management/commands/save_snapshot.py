from django_netjsongraph.management.commands import BaseSaveSnapshotCommand

from ...models import Topology


class Command(BaseSaveSnapshotCommand):
    topology_model = Topology
