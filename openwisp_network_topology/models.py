from .base.link import AbstractLink
from .base.node import AbstractNode
from .base.snapshot import AbstractSnapshot
from .base.topology import AbstractTopology


class Link(AbstractLink):
    class Meta(AbstractLink.Meta):
        abstract = False


class Node(AbstractNode):
    class Meta(AbstractNode.Meta):
        abstract = False


class Snapshot(AbstractSnapshot):
    class Meta(AbstractSnapshot.Meta):
        abstract = False


class Topology(AbstractTopology):
    class Meta(AbstractTopology.Meta):
        abstract = False
