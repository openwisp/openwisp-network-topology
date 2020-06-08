import json
from collections import OrderedDict
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from netdiff import NetJsonParser, diff
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.mixins import OrgMixin
from openwisp_utils.base import KeyField, TimeStampedEditableModel

from ..contextmanagers import log_failure
from ..settings import PARSERS, TIMEOUT
from ..utils import print_info

STRATEGIES = (('fetch', _('FETCH')), ('receive', _('RECEIVE')))


class AbstractTopology(OrgMixin, TimeStampedEditableModel):

    label = models.CharField(_('label'), max_length=64)
    parser = models.CharField(
        _('format'),
        choices=PARSERS,
        max_length=128,
        help_text=_('Select topology format'),
    )
    strategy = models.CharField(
        _('strategy'), max_length=16, choices=STRATEGIES, default='fetch', db_index=True
    )
    # fetch strategy
    url = models.URLField(
        _('url'),
        blank=True,
        help_text=_('Topology data will be fetched from this URL' ' (FETCH strategy)'),
    )
    # receive strategy
    key = KeyField(
        unique=False,
        db_index=False,
        help_text=_('key needed to update topology from nodes '),
        verbose_name=_('key'),
        blank=True,
    )
    # receive strategy
    expiration_time = models.PositiveIntegerField(
        _('expiration time'),
        default=0,
        help_text=_(
            '"Expiration Time" in seconds: setting this to 0 will immediately mark missing links '
            'as down; a value higher than 0 will delay marking missing links as down until the '
            '"modified" field of a link is older than "Expiration Time"'
        ),
    )
    published = models.BooleanField(
        _('published'),
        default=True,
        help_text=_(
            'Unpublished topologies won\'t be updated or ' 'shown in the visualizer'
        ),
    )

    # the following fields will be filled automatically
    protocol = models.CharField(_('protocol'), max_length=64, blank=True)
    version = models.CharField(_('version'), max_length=24, blank=True)
    revision = models.CharField(_('revision'), max_length=64, blank=True)
    metric = models.CharField(_('metric'), max_length=24, blank=True)

    class Meta:
        verbose_name_plural = _('topologies')
        abstract = True

    def __str__(self):
        return '{0} - {1}'.format(self.label, self.get_parser_display())

    def get_absolute_url(self):
        return reverse('topology_detail', args=[self.pk])

    def clean(self):
        if self.strategy == 'fetch' and not self.url:
            raise ValidationError(
                {'url': [_('an url must be specified when using FETCH strategy')]}
            )
        elif self.strategy == 'receive' and not self.key:
            raise ValidationError(
                {'key': [_('a key must be specified when using RECEIVE strategy')]}
            )

    @cached_property
    def parser_class(self):
        return import_string(self.parser)

    @property
    def link_model(self):
        return self.link_set.model

    @property
    def node_model(self):
        return self.node_set.model

    @property
    def snapshot_model(self):
        return self.snapshot_set.model

    def get_topology_data(self, data=None):
        """
        gets latest topology data
        """
        # if data is ``None`` it will be fetched from ``self.url``
        latest = self.parser_class(data=data, url=self.url, timeout=TIMEOUT)
        # update topology attributes if needed
        changed = False
        for attr in ['protocol', 'version', 'metric']:
            latest_attr = getattr(latest, attr)
            if getattr(self, attr) != latest_attr:
                setattr(self, attr, latest_attr)
                changed = True
        if changed:
            self.save()
        return latest

    def diff(self, data=None):
        """ shortcut to netdiff.diff """
        # if we get an instance of ``self.parser_class`` it means
        # ``self.get_topology_data`` has already been executed by ``receive``
        if isinstance(data, self.parser_class):
            latest = data
        else:
            latest = self.get_topology_data(data)
        current = NetJsonParser(self.json(dict=True, omit_down=True))
        return diff(current, latest)

    def json(self, dict=False, omit_down=False, **kwargs):
        """ returns a dict that represents a NetJSON NetworkGraph object """
        nodes = []
        links = []
        link_queryset = self.link_set.select_related('source', 'target')
        # needed to detect links coming back online
        if omit_down:
            link_queryset = link_queryset.filter(status='up')
        # populate graph
        for link in link_queryset:
            links.append(link.json(dict=True))
        for node in self.node_set.all():
            nodes.append(node.json(dict=True))
        netjson = OrderedDict(
            (
                ('type', 'NetworkGraph'),
                ('protocol', self.protocol),
                ('version', self.version),
                ('metric', self.metric),
                ('label', self.label),
                ('id', str(self.id)),
                ('parser', self.parser),
                ('created', self.created),
                ('modified', self.modified),
                ('nodes', nodes),
                ('links', links),
            )
        )
        if dict:
            return netjson
        return json.dumps(netjson, cls=JSONEncoder, **kwargs)

    def _create_node(self, **kwargs):
        options = dict(organization=self.organization, topology=self)
        options.update(kwargs)
        node = self.node_model(**options)
        return node

    def _create_link(self, **kwargs):
        options = dict(organization=self.organization, topology=self)
        options.update(kwargs)
        link = self.link_model(**options)
        return link

    def update(self, data=None):
        """
        Updates topology
        Links are not deleted straightaway but set as "down"
        """
        Link, Node = self.link_model, self.node_model
        diff = self.diff(data)

        status = {'added': 'up', 'removed': 'down', 'changed': 'up'}
        action = {'added': 'add', 'changed': 'change', 'removed': 'remove'}

        try:
            added_nodes = diff['added']['nodes']
        except TypeError:
            added_nodes = []

        for node_dict in added_nodes:
            node = Node.count_address(node_dict['id'], topology=self)
            # if node exists skip to next iteration
            if node:  # pragma no cover
                continue
            # if node doesn't exist create new
            addresses = [node_dict['id']]
            addresses += node_dict.get('local_addresses', [])
            properties = node_dict.get('properties', {})
            node = self._create_node(addresses=addresses, properties=properties)
            if 'label' in node_dict:
                node.label = node_dict.get('label')
            node.full_clean()
            node.save()

        for section, graph in sorted(diff.items()):
            # if graph is empty skip to next one
            if not graph:
                continue
            for link_dict in graph['links']:
                changed = False
                link = Link.get_from_nodes(
                    link_dict['source'], link_dict['target'], topology=self
                )
                # if link does not exist create new
                if not link:
                    source = Node.get_from_address(link_dict['source'], self)
                    target = Node.get_from_address(link_dict['target'], self)
                    link = self._create_link(
                        source=source,
                        target=target,
                        cost=link_dict['cost'],
                        properties=link_dict.get('properties', {}),
                        topology=self,
                    )
                    changed = True
                # if status of link is changed
                if self.link_status_changed(link, status[section]):
                    link.status = status[section]
                    changed = True
                # if cost of link has changed
                if link.cost != link_dict['cost']:
                    link.cost = link_dict['cost']
                    changed = True
                # perform writes only if needed
                if changed:
                    with log_failure(action[section], link):
                        link.full_clean()
                        link.save()

    def save_snapshot(self, **kwargs):
        """
        Saves the snapshot of topology
        """
        Snapshot = self.snapshot_model
        date = datetime.now().date()
        options = dict(organization=self.organization, topology=self, date=date)
        options.update(kwargs)
        try:
            s = Snapshot.objects.get(**options)
        except Snapshot.DoesNotExist:
            s = Snapshot(**options)
        s.data = self.json()
        s.save()

    def link_status_changed(self, link, status):
        """
        determines if link status has changed,
        takes in consideration also ``strategy`` and ``expiration_time``
        """
        status_changed = link.status != status
        # if status has not changed return ``False`` immediately
        if not status_changed:
            return False
        # if using fetch strategy or
        # using receive strategy and link is coming back up or
        # receive strategy and ``expiration_time == 0``
        elif self.strategy == 'fetch' or status == 'up' or self.expiration_time == 0:
            return True
        # if using receive strategy and expiration_time of link has expired
        elif link.modified < (now() - timedelta(seconds=self.expiration_time)):
            return True
        # if using receive strategy and expiration_time of link has not expired
        return False

    def receive(self, data):
        """
        Receive topology data (RECEIVE strategy)
        expiration_time at 0 means:
          "if a link is missing, mark it as down immediately"
        expiration_time > 0 means:
          "if a link is missing, wait expiration_time seconds before marking it as down"
        """
        if self.expiration_time > 0:
            data = self.get_topology_data(data)
            Link = self.link_model
            netjson = data.json(dict=True)
            # update last modified date of all received links
            for link_dict in netjson['links']:
                link = Link.get_from_nodes(
                    link_dict['source'], link_dict['target'], topology=self
                )
                if link:
                    link.save()
        self.update(data)

    @classmethod
    def update_all(cls, label=None):
        """
        - updates topologies
        - logs failures
        - calls delete_expired_links()
        """
        queryset = cls.objects.filter(published=True, strategy='fetch')
        if label:
            queryset = queryset.filter(label__icontains=label)
        for topology in queryset:
            print_info('Updating topology {0}'.format(topology))
            with log_failure('update', topology):
                topology.update()
        cls().link_model.delete_expired_links()
        cls().node_model.delete_expired_nodes()

    @classmethod
    def save_snapshot_all(cls, label=None):
        """
        - save snapshots of topoogies
        - logs failures
        """
        queryset = cls.objects.filter(published=True)
        if label:
            queryset = queryset.filter(label__icontains=label)
        for topology in queryset:
            print_info('Saving topology {0}'.format(topology))
            with log_failure('save_snapshot', topology):
                topology.save_snapshot()
