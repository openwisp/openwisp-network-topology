import logging
from ipaddress import ip_address

from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string
from swapper import get_model_name, load_model

from openwisp_utils.base import UUIDModel

logger = logging.getLogger(__name__)

trigger_device_checks_path = 'openwisp_monitoring.device.tasks.trigger_device_checks'


class AbstractDeviceNode(UUIDModel):
    node = models.OneToOneField(
        get_model_name('topology', 'Node'), on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        get_model_name('config', 'Device'), on_delete=models.CASCADE
    )

    # relations will be auto-created only for these parsers
    ENABLED_PARSERS = {
        'netdiff.OpenvpnParser': {
            'auto_create': 'auto_create_openvpn',
            'link_down': 'link_down_openvpn',
            'link_up': 'link_up_openvpn',
        }
    }

    class Meta:
        abstract = True
        unique_together = ('node', 'device')

    @classmethod
    def auto_create(cls, node):
        """
        Attempts to perform automatic creation of DeviceNode objects.
        The right action to perform depends on the Topology used.
        """
        opts = cls.ENABLED_PARSERS.get(node.topology.parser)
        if opts:
            return getattr(cls, opts['auto_create'])(node)

    @classmethod
    def auto_create_openvpn(cls, node):
        """
        Implementation of the integration between
        controller and network-topology modules
        when using OpenVPN (using the common name)
        """
        common_name = node.properties.get('common_name')
        if not common_name:
            return

        Device = load_model('config', 'Device')
        device_filter = models.Q(config__vpnclient__cert__common_name=common_name)
        if node.organization_id:
            device_filter &= models.Q(organization_id=node.organization_id)
        device = (
            Device.objects.only(
                'id', 'name', 'last_ip', 'management_ip', 'organization_id'
            )
            .filter(device_filter)
            .first()
        )
        if not device:
            return

        device_node = cls(device=device, node=node)
        try:
            device_node.full_clean()
            device_node.save()
            # Update organization of the node. This is required
            # when topology is shared.
            if node.organization_id is None:
                node.organization_id = device.organization_id
                node.save(update_fields=['organization_id'])
        except Exception:
            logger.exception('Exception raised during auto_create_openvpn')
            return
        else:
            logger.info(f'DeviceNode relation created for {node.label} - {device.name}')
            return device_node

    def link_action(self, link, status):
        """
        Performs clean-up operations when link goes down.
        The right action to perform depends on the Topology used.
        """
        opts = self.ENABLED_PARSERS.get(link.topology.parser)
        if opts:
            key = f'link_{status}'
            return getattr(self, opts[key])()

    def link_down_openvpn(self):
        """
        Link down action for OpenVPN
        """
        self.device.management_ip = None
        self.device.save()

    def link_up_openvpn(self):
        """
        Link up action for OpenVPN
        """
        addresses = self.node.addresses
        try:
            address = ip_address(addresses[1])
        except (IndexError, ValueError) as e:
            addresses = ', '.join(addresses)
            logger.warning(
                f'{e.__class__.__name__} raised while processing addresses: {addresses}'
            )
        else:
            self.device.management_ip = str(address)
            self.device.save()

    @classmethod
    def filter_by_link(cls, link):
        """
        Returns a queryset which looks for a DeviceNode which is related
        to the specified Link instance.
        """
        return cls.objects.filter(
            models.Q(node__source_link_set__pk=link.pk)
            | models.Q(node__target_link_set__pk=link.pk)
        ).select_related('device', 'node')

    @classmethod
    def trigger_device_updates(cls, link):
        """
        Used to refresh controller and monitoring information
        whenever the status of a link changes
        """
        if link.topology.parser not in cls.ENABLED_PARSERS:
            return
        for device_node in cls.filter_by_link(link):
            device_node.link_action(link, link.status)
            # triggers monitoring checks if OpenWISP Monitoring is enabled
            if 'openwisp_monitoring.device' in settings.INSTALLED_APPS:
                run_checks = import_string(trigger_device_checks_path)
                run_checks.delay(device_node.device.pk, recovery=link.status == 'up')
