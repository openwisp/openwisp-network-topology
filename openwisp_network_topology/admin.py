from django.contrib import admin

from openwisp_users.multitenancy import (
    MultitenantAdminMixin,
    MultitenantOrgFilter,
    MultitenantRelatedOrgFilter,
)

from .base.admin import AbstractLinkAdmin, AbstractNodeAdmin, AbstractTopologyAdmin
from .models import Link, Node, Topology


class TopologyAdmin(AbstractTopologyAdmin):
    model = Topology


class NodeAdmin(AbstractNodeAdmin):
    model = Node


class LinkAdmin(AbstractLinkAdmin):
    model = Link


admin.site.register(Link, LinkAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Topology, TopologyAdmin)
