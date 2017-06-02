from django.contrib import admin
from django_netjsongraph.base.admin import (AbstractLinkAdmin,
                                            AbstractNodeAdmin,
                                            AbstractTopologyAdmin)

from .base.admin import MultitenantAdminMixin
from .models import Link, Node, Topology


class TopologyAdmin(MultitenantAdminMixin, AbstractTopologyAdmin):
    model = Topology


class NodeAdmin(MultitenantAdminMixin, AbstractNodeAdmin):
    model = Node


class LinkAdmin(MultitenantAdminMixin, AbstractLinkAdmin):
    model = Link


admin.site.register(Link, LinkAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Topology, TopologyAdmin)
