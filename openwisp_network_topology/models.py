import swapper

from .base.link import AbstractLink
from .base.node import AbstractNode
from .base.snapshot import AbstractSnapshot
from .base.topology import AbstractTopology


class Link(AbstractLink):
    class Meta(AbstractLink.Meta):
        abstract = False
        swappable = swapper.swappable_setting('topology', 'Link')


class Node(AbstractNode):
    class Meta(AbstractNode.Meta):
        abstract = False
        swappable = swapper.swappable_setting('topology', 'Node')


class Snapshot(AbstractSnapshot):
    class Meta(AbstractSnapshot.Meta):
        abstract = False
        swappable = swapper.swappable_setting('topology', 'Snapshot')


class Topology(AbstractTopology):
    class Meta(AbstractTopology.Meta):
        abstract = False
        swappable = swapper.swappable_setting('topology', 'Topology')
