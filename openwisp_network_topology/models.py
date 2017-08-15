from django.db import models
from django_netjsongraph.base.link import AbstractLink
from django_netjsongraph.base.node import AbstractNode
from django_netjsongraph.base.snapshot import AbstractSnapshot
from django_netjsongraph.base.topology import AbstractTopology

from openwisp_users.mixins import OrgMixin


class Link(OrgMixin, AbstractLink):
    topology = models.ForeignKey('topology.Topology')
    source = models.ForeignKey('topology.Node', related_name='source_link_set')
    target = models.ForeignKey('topology.Node', related_name='source_target_set')

    class Meta(AbstractLink.Meta):
        abstract = False


class Node(OrgMixin, AbstractNode):
    topology = models.ForeignKey('topology.Topology')

    class Meta(AbstractNode.Meta):
        abstract = False


class Snapshot(OrgMixin, AbstractSnapshot):
    topology = models.ForeignKey('topology.Topology')

    class Meta(AbstractSnapshot.Meta):
        abstract = False


class Topology(OrgMixin, AbstractTopology):
    def _create_node(self, **kwargs):
        options = dict(organization=self.organization,
                       topology=self)
        options.update(kwargs)
        return self.node_model(**options)

    def _create_link(self, **kwargs):
        options = dict(organization=self.organization,
                       topology=self)
        options.update(kwargs)
        return self.link_model(**options)

    def save_snapshot(self, **kwargs):
        options = dict(organization=self.organization)
        options.update(kwargs)
        super(Topology, self).save_snapshot(**options)

    class Meta(AbstractTopology.Meta):
        abstract = False
