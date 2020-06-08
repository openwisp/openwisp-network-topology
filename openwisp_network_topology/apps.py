import swapper
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .settings import SIGNALS


class OpenwispNetworkTopologyConfig(AppConfig):
    name = 'openwisp_network_topology'
    label = 'topology'
    verbose_name = _('Network Topology')

    def ready(self, *args, **kwargs):
        if SIGNALS:  # pragma: nocover
            __import__(SIGNALS)
        self.add_default_menu_items()

    def add_default_menu_items(self):
        menu_setting = 'OPENWISP_DEFAULT_ADMIN_MENU_ITEMS'
        items = [{'model': swapper.get_model_name('topology', 'Topology')}]
        if not hasattr(settings, menu_setting):
            setattr(settings, menu_setting, items)
        else:
            current_menu = getattr(settings, menu_setting)
            current_menu += items
