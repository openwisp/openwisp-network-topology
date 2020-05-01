from ...models import Topology
from . import BaseUpdateCommand


class Command(BaseUpdateCommand):
    topology_model = Topology
