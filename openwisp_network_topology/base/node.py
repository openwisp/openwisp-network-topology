import json
from collections import OrderedDict
from copy import deepcopy
from datetime import timedelta

import swapper
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.mixins import ShareableOrgMixin
from openwisp_utils.base import TimeStampedEditableModel

from .. import settings as app_settings
from ..signals import update_topology
from ..utils import print_info


class AbstractNode(ShareableOrgMixin, TimeStampedEditableModel):
    """
    NetJSON NetworkGraph Node Object implementation
    """

    topology = models.ForeignKey(
        swapper.get_model_name("topology", "Topology"), on_delete=models.CASCADE
    )
    label = models.CharField(max_length=64, blank=True)
    # netjson ID and local_addresses
    addresses = JSONField(default=[], blank=True)
    properties = JSONField(
        default=dict,
        blank=True,
        load_kwargs={"object_pairs_hook": OrderedDict},
        dump_kwargs={"indent": 4, "cls": JSONEncoder},
    )
    user_properties = JSONField(
        verbose_name=_("user defined properties"),
        help_text=_("If you need to add additional data to this node use this field"),
        default=dict,
        blank=True,
        load_kwargs={"object_pairs_hook": OrderedDict},
        dump_kwargs={"indent": 4, "cls": JSONEncoder},
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def full_clean(self, *args, **kwargs):
        self.organization_id = self.get_organization_id()
        return super().full_clean(*args, **kwargs)

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
        return self.label or self.netjson_id or ""

    def get_name(self):
        """
        May be overridden/monkey patched to get the node name
        from other sources (e.g: device name in openwisp-controller)
        """
        return self.name

    def get_organization_id(self):
        """
        May be overridden/monkey patched to get the node organization
        from other sources (e.g: device organization_id in openwisp-controller)
        """
        # Node will get organization of topology if it is unspecified.
        if self.organization_id is None:
            return self.topology.organization_id
        else:
            # Non-shared node can belong to shared topology. But,
            # a shared node cannot belong to non-shared topology.
            if (
                self.topology.organization_id is not None
                and self.topology.organization_id != self.organization_id
            ):
                raise ValidationError(
                    _("node should have same organization as topology.")
                )
            return self.organization_id

    def json(self, dict=False, original=False, **kwargs):
        """
        Returns a NetJSON NetworkGraph Node object.

        If ``original`` is passed, the data will be returned
        as it has been collected from the network (used when
        doing the comparison).
        """
        netjson = OrderedDict({"id": self.netjson_id})
        label = self.get_name()
        if label:
            netjson["label"] = label
        for attr in ["local_addresses", "properties"]:
            value = getattr(self, attr)
            if value or attr == "properties":
                netjson[attr] = deepcopy(value)
        if not original:
            netjson["properties"].update(deepcopy(self.user_properties))
            netjson["properties"]["created"] = JSONEncoder().default(self.created)
            netjson["properties"]["modified"] = JSONEncoder().default(self.modified)
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
        deletes nodes that have not been connected to the network
        for more than the amount of days specified in
        ``OPENWISP_NETWORK_TOPOLOGY_NODE_EXPIRATION``
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
                print_info("Deleting {0} expired nodes".format(expired_nodes_length))
                for node in expired_nodes:
                    node.delete()

    @classmethod
    def get_queryset(cls, qs):
        """admin list queryset"""
        return qs.select_related("organization", "topology")


@receiver(post_save, sender=swapper.get_model_name("topology", "Node"))
@receiver(post_delete, sender=swapper.get_model_name("topology", "Node"))
def send_topology_signal(sender, instance, **kwargs):
    update_topology.send(sender=sender, topology=instance.topology)
