from django.db import models

from openwisp_network_topology.base.link import AbstractLink
from openwisp_network_topology.base.node import AbstractNode
from openwisp_network_topology.base.snapshot import AbstractSnapshot
from openwisp_network_topology.base.topology import AbstractTopology


class DetailsModel(models.Model):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class Link(DetailsModel, AbstractLink):
    class Meta(AbstractLink.Meta):
        abstract = False


class Node(DetailsModel, AbstractNode):
    class Meta(AbstractNode.Meta):
        abstract = False


class Snapshot(DetailsModel, AbstractSnapshot):
    class Meta(AbstractSnapshot.Meta):
        abstract = False


class Topology(DetailsModel, AbstractTopology):
    class Meta(AbstractTopology.Meta):
        abstract = False
