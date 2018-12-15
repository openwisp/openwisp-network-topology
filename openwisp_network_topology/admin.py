from django.contrib import admin
from django_netjsongraph.base.admin import AbstractLinkAdmin, AbstractNodeAdmin, AbstractTopologyAdmin

from openwisp_users.multitenancy import (MultitenantAdminMixin, MultitenantOrgFilter,
                                         MultitenantRelatedOrgFilter)

from .models import Link, Node, Topology


class TopologyAdmin(MultitenantAdminMixin, AbstractTopologyAdmin):
    model = Topology


TopologyAdmin.list_display += ('organization',)
TopologyAdmin.list_filter += (('organization', MultitenantOrgFilter),)
TopologyAdmin.fields.insert(1, 'organization')


class NodeAdmin(MultitenantAdminMixin, AbstractNodeAdmin):
    model = Node
    list_display = ['name', 'organization', 'topology', 'addresses']
    list_filter = [('organization', MultitenantOrgFilter),
                   ('topology', MultitenantRelatedOrgFilter)]
    multitenant_shared_relations = ('topology',)
    fields = ['label', 'organization', 'addresses', 'properties', 'topology',
              'created', 'modified']


class LinkAdmin(MultitenantAdminMixin, AbstractLinkAdmin):
    model = Link
    list_display = ['__str__', 'organization', 'topology', 'status', 'cost',
                    'cost_text']
    list_filter = ['status',
                   ('organization', MultitenantOrgFilter),
                   ('topology', MultitenantRelatedOrgFilter)]
    multitenant_shared_relations = ('topology', 'source', 'target')
    fields = ['organization', 'cost', 'cost_text', 'status', 'properties',
              'topology', 'source', 'target', 'created', 'modified']


admin.site.register(Link, LinkAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Topology, TopologyAdmin)
