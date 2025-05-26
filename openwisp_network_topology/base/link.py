import json
from collections import OrderedDict
from datetime import timedelta

import swapper
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from model_utils import Choices
from model_utils.fields import StatusField
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.mixins import ShareableOrgMixin
from openwisp_utils.base import TimeStampedEditableModel

from .. import settings as app_settings
from ..signals import update_topology
from ..utils import link_status_changed, print_info


class AbstractLink(ShareableOrgMixin, TimeStampedEditableModel):
    """
    NetJSON NetworkGraph Link Object implementation
    """

    topology = models.ForeignKey(
        swapper.get_model_name("topology", "Topology"), on_delete=models.CASCADE
    )
    source = models.ForeignKey(
        swapper.get_model_name("topology", "Node"),
        related_name="source_link_set",
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        swapper.get_model_name("topology", "Node"),
        related_name="target_link_set",
        on_delete=models.CASCADE,
    )
    cost = models.FloatField()
    cost_text = models.CharField(max_length=24, blank=True)
    STATUS = Choices("up", "down")
    status = StatusField()
    properties = JSONField(
        default=dict,
        blank=True,
        load_kwargs={"object_pairs_hook": OrderedDict},
        dump_kwargs={"indent": 4, "cls": JSONEncoder},
    )
    user_properties = JSONField(
        verbose_name=_("user defined properties"),
        help_text=_("If you need to add additional data to this link use this field"),
        default=dict,
        blank=True,
        load_kwargs={"object_pairs_hook": OrderedDict},
        dump_kwargs={"indent": 4, "cls": JSONEncoder},
    )
    status_changed = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_status = self.status

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status != self._initial_status:
            self.send_status_changed_signal()
            self.status_changed = now()
        self._initial_status = self.status

    def __str__(self):
        return "{0} - {1}".format(self.source.get_name(), self.target.get_name())

    def full_clean(self, *args, **kwargs):
        self.validate_organization()
        self.validate_topology()
        return super().full_clean(*args, **kwargs)

    def clean(self):
        if self.source == self.target or self.source_id == self.target_id:
            raise ValidationError(_("source and target must not be the same"))
        if self.properties is None:
            self.properties = {}
        # these properties are auto-generated and should not be saved
        for attr in ["status", "status_changed", "modified", "created"]:
            if attr in self.properties:
                del self.properties[attr]

    def validate_topology(self):
        errors = {}
        if self.source.topology_id != self.topology_id:
            errors["source"] = _("Source node and link should have same topology.")
        if self.target.topology_id != self.topology_id:
            errors["target"] = _("Target node and link should have same topology.")
        if errors:
            raise ValidationError(errors)

    def validate_organization(self):
        if self.topology.organization_id is None:
            # Shared link is only created between nodes of
            # two different organizations.
            if self.source.organization_id == self.target.organization_id:
                self.organization_id = self.source.organization_id
            else:
                self.organization_id = None
        else:
            errors = {}
            if self.source.organization_id != self.topology.organization_id:
                errors.update(
                    {
                        "source": _(
                            "Source node and topology should have same organization."
                        )
                    }
                )
            if self.target.organization_id != self.topology.organization_id:
                errors.update(
                    {
                        "target": _(
                            "Target node and topology should have same organization."
                        )
                    }
                )
            if errors:
                raise ValidationError(errors)
            self.organization_id = self.topology.organization_id

    def json(self, dict=False, original=False, **kwargs):
        """
        Returns a NetJSON NetworkGraph Link object.

        If ``original`` is passed, the data will be returned
        as it has been collected from the network (used when
        doing the comparison).
        """
        netjson = OrderedDict(
            (
                ("source", self.source.netjson_id),
                ("target", self.target.netjson_id),
                ("cost", self.cost),
                ("cost_text", self.cost_text or ""),
            )
        )
        # properties contain status by default
        properties = OrderedDict()
        if self.properties:
            properties.update(self.properties)
        if not original:
            properties.update(self.user_properties)
            properties["status"] = self.status
            properties["status_changed"] = self.status_changed
            properties["created"] = self.created
            properties["modified"] = self.modified
        netjson["properties"] = properties
        if dict:
            return netjson
        return json.dumps(netjson, cls=JSONEncoder, **kwargs)

    def send_status_changed_signal(self):
        link_status_changed.send(sender=self.__class__, link=self)

    @classmethod
    def get_from_nodes(cls, source, target, topology):
        """
        Find link between source and target,
        (or vice versa, order is irrelevant).
        Source and target nodes must already exist.
        :param source: string
        :param target: string
        :param topology: Topology instance
        :returns: Link object or None
        """
        source = '"{}"'.format(source)
        target = '"{}"'.format(target)
        q = Q(
            source__addresses__contains=source, target__addresses__contains=target
        ) | Q(source__addresses__contains=target, target__addresses__contains=source)
        return cls.objects.filter(q).filter(topology=topology).first()

    @classmethod
    def delete_expired_links(cls):
        """
        deletes links that have been down for more than
        the amount of days specified in
        ``OPENWISP_NETWORK_TOPOLOGY_LINK_EXPIRATION``
        """
        LINK_EXPIRATION = app_settings.LINK_EXPIRATION
        if LINK_EXPIRATION not in [False, None]:
            expiration_date = now() - timedelta(days=int(LINK_EXPIRATION))
            expired_links = cls.objects.filter(
                status="down", modified__lt=expiration_date
            )
            expired_links_length = len(expired_links)
            if expired_links_length:
                print_info("Deleting {0} expired links".format(expired_links_length))
                for link in expired_links:
                    link.delete()

    @classmethod
    def get_queryset(cls, qs):
        """admin list queryset"""
        return qs.select_related("organization", "topology", "source", "target")


@receiver(post_save, sender=swapper.get_model_name("topology", "Link"))
@receiver(post_delete, sender=swapper.get_model_name("topology", "Link"))
def send_topology_signal(sender, instance, **kwargs):
    update_topology.send(sender=sender, topology=instance.topology)
