from django.conf import settings
from django_netjsongraph.apps import DjangoNetjsongraphConfig


class OpenwispNetworkTopologyConfig(DjangoNetjsongraphConfig):
    name = 'openwisp_network_topology'
    label = 'topology'

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)
        self.add_default_menu_items()

    def add_default_menu_items(self):
        menu_setting = 'OPENWISP_DEFAULT_ADMIN_MENU_ITEMS'
        items = [
            {'model': 'topology.Topology'}
        ]
        if not hasattr(settings, menu_setting):
            setattr(settings, menu_setting, items)
        else:
            current_menu = getattr(settings, menu_setting)
            current_menu += items
