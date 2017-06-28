from django.utils.translation import ugettext_lazy as _
from django_netjsongraph.apps import DjangoNetjsongraphConfig


class OpenwispNetworkTopologyConfig(DjangoNetjsongraphConfig):
    name = 'openwisp_network_topology'
    label = 'openwisp_network_topology'
    verbose_name = _('OpenWISP Network Topology')
