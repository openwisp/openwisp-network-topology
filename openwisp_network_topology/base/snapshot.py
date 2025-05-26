import swapper
from django.db import models
from django.utils.translation import gettext_lazy as _

from openwisp_utils.base import TimeStampedEditableModel


class AbstractSnapshot(TimeStampedEditableModel):
    """
    NetJSON NetworkGraph Snapshot implementation
    """

    topology = models.ForeignKey(
        swapper.get_model_name("topology", "Topology"), on_delete=models.CASCADE
    )
    data = models.TextField(blank=False)
    date = models.DateField(auto_now=True)

    class Meta:
        verbose_name_plural = _("snapshots")
        abstract = True

    def __str__(self):
        return "{0}: {1}".format(self.topology.label, self.date)
