from ...models import Topology
from . import BaseSaveSnapshotCommand


class Command(BaseSaveSnapshotCommand):
    topology_model = Topology
