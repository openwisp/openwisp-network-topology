import json
from collections import OrderedDict
from datetime import timedelta

import swapper
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now
from jsonfield import JSONField
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.mixins import OrgMixin
from openwisp_utils.base import TimeStampedEditableModel

from .. import settings as app_settings
from ..utils import print_info


class AbstractNode(OrgMixin, TimeStampedEditableModel):
    """
    NetJSON NetworkGraph Node Object implementation
    """

    topology = models.ForeignKey(
        swapper.get_model_name('topology', 'Topology'), on_delete=models.CASCADE
    )
    label = models.CharField(max_length=64, blank=True)
    # netjson ID and local_addresses
    addresses = JSONField(default=[], blank=True)
    properties = JSONField(
        default=dict,
        blank=True,
        load_kwargs={'object_pairs_hook': OrderedDict},
        dump_kwargs={'indent': 4, 'cls': JSONEncoder},
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        if self.properties is None:
            self.properties = {}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def netjson_id(self):
        if len(self.addresses) > 0:
            return self.addresses[0]

    @cached_property
    def local_addresses(self):
        if len(self.addresses) > 1:
            return self.addresses[1:]

    @property
    def name(self):
        return self.label or self.netjson_id or ''

    def json(self, dict=False, **kwargs):
        """
        returns a NetJSON NetworkGraph Node object
        """
        netjson = OrderedDict({'id': self.netjson_id})
        for attr in ['label', 'local_addresses', 'properties']:
            value = getattr(self, attr)
            if value or attr == 'properties':
                netjson[attr] = value
        netjson['properties']['created'] = JSONEncoder().default(self.created)
        netjson['properties']['modified'] = JSONEncoder().default(self.modified)
        if dict:
            return netjson
        return json.dumps(netjson, cls=JSONEncoder, **kwargs)

    @classmethod
    def get_from_address(cls, address, topology):
        """
        Find node from one of its addresses and its topology.
        :param address: string
        :param topology: Topology instance
        :returns: Node object or None
        """
        address = '"{}"'.format(address)
        return cls.objects.filter(
            topology=topology, addresses__contains=address
        ).first()

    @classmethod
    def count_address(cls, address, topology):
        """
        Count nodes with the specified address and topology.
        :param address: string
        :param topology: Topology instance
        :returns: int
        """
        address = '"{}"'.format(address)
        return cls.objects.filter(
            topology=topology, addresses__contains=address
        ).count()

    @classmethod
    def delete_expired_nodes(cls):
        """
        deletes nodes that have not been  connected to the network
        for more than ``NETJSONGRAPH__EXPIRATION`` days
        """
        NODE_EXPIRATION = app_settings.NODE_EXPIRATION
        LINK_EXPIRATION = app_settings.LINK_EXPIRATION
        if NODE_EXPIRATION not in [False, None] and LINK_EXPIRATION not in [
            False,
            None,
        ]:
            expiration_date = now() - timedelta(days=int(NODE_EXPIRATION))
            expired_nodes = cls.objects.filter(
                modified__lt=expiration_date,
                source_link_set__isnull=True,
                target_link_set__isnull=True,
            )
            expired_nodes_length = len(expired_nodes)
            if expired_nodes_length:
                print_info('Deleting {0} expired nodes'.format(expired_nodes_length))
                for node in expired_nodes:
                    node.delete()
