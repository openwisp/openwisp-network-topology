from django.db import models
from django_netjsongraph.base.link import AbstractLink
from django_netjsongraph.base.node import AbstractNode
from django_netjsongraph.base.topology import AbstractTopology

from openwisp_users.mixins import OrgMixin


class Link(OrgMixin, AbstractLink):
    topology = models.ForeignKey('Topology')
    source = models.ForeignKey('Node',
                               related_name='source_link_set')
    target = models.ForeignKey('Node',
                               related_name='source_target_set')

    class Meta(AbstractLink.Meta):
        abstract = False


class Node(OrgMixin, AbstractNode):
    topology = models.ForeignKey('Topology')

    class Meta(AbstractNode.Meta):
        abstract = False


class Topology(OrgMixin, AbstractTopology):
    class Meta(AbstractTopology.Meta):
        abstract = False
