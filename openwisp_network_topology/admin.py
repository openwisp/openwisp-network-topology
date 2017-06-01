from django.contrib import admin

from django_netjsongraph.base.admin import (AbstractTopologyAdmin,
                                            AbstractNodeAdmin,
                                            AbstractLinkAdmin)
from openwisp_users.admin import OrganizationAdmin as BaseOrganizationAdmin
from openwisp_users.models import Organization

from .base.admin import (AlwaysHasChangedMixin,
                         MultitenantAdminMixin,
                         MultitenantOrgFilter,
                         MultitenantTopologyFilter)
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
