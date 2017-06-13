from django_netjsongraph.apps import DjangoNetjsongraphConfig
from django.utils.translation import ugettext_lazy as _


class OpenwispNetworkTopologyConfig(DjangoNetjsongraphConfig):
    name = 'openwisp_network_topology'
    label = 'openwisp_network_topology'
    verbose_name = _('OpenWISP Network Topology')
