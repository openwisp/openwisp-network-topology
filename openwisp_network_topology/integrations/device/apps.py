from importlib import import_module

import swapper
from django.apps import AppConfig
from django.db import transaction
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from openwisp_monitoring.device.signals import device_metrics_received

from ...utils import link_status_changed
from . import settings as app_settings
from .tasks import create_device_node_relation, trigger_device_updates


class OpenwispTopologyDeviceConfig(AppConfig):
    name = 'openwisp_network_topology.integrations.device'
    label = 'topology_device'
    verbose_name = _('Topology Device Integration')

    def ready(self):
        self.connect_signals()
        self.override_node_label()

    def connect_signals(self):
        Node = swapper.load_model('topology', 'Node')
        Link = swapper.load_model('topology', 'Link')
        WifiMesh = swapper.load_model('topology_device', 'WifiMesh')
        DeviceData = swapper.load_model('device_monitoring', 'DeviceData')

        post_save.connect(
            self.create_device_rel, sender=Node, dispatch_uid='node_to_device_rel'
        )
        link_status_changed.connect(
            self.link_status_changed_receiver,
            sender=Link,
            dispatch_uid='controller_integration_link_status_chaged',
        )
        if app_settings.WIFI_MESH_INTEGRATION:
            device_metrics_received.connect(
                WifiMesh.create_wifi_mesh_topology,
                sender=DeviceData,
                dispatch_uid='create_wifi_mesh_topology',
            )

    @classmethod
    def create_device_rel(cls, instance, created, **kwargs):
        if not created:
            return
        transaction.on_commit(lambda: create_device_node_relation.delay(instance.pk))

    @classmethod
    def link_status_changed_receiver(cls, link, **kwargs):
        transaction.on_commit(lambda: trigger_device_updates.delay(link.pk))

    def override_node_label(self):
        import_module('openwisp_network_topology.integrations.device.overrides')
