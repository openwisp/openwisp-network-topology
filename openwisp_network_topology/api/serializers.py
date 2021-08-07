import json
from collections import OrderedDict

import swapper
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.utils.encoders import JSONEncoder

from openwisp_users.api.mixins import FilterSerializerByOrgManaged
from openwisp_utils.api.serializers import ValidatedModelSerializer

Node = swapper.load_model('topology', 'Node')
Link = swapper.load_model('topology', 'Link')
Topology = swapper.load_model('topology', 'Topology')


class NetworkCollectionSerializer(serializers.ListSerializer):
    """
    NetJSON NetworkCollection
    """

    @property
    def data(self):
        return super(serializers.ListSerializer, self).data

    def to_representation(self, data):
        return OrderedDict(
            (
                ('type', 'NetworkCollection'),
                ('collection', super().to_representation(data)),
            )
        )


class TopologySerializer(ValidatedModelSerializer):
    class Meta:
        model = Topology
        fields = '__all__'


class NetworkGraphSerializer(ValidatedModelSerializer):
    """
    NetJSON NetworkGraph
    """

    def to_representation(self, obj):
        if self.context['request'].method == 'POST':
            serializer = TopologySerializer(self.instance)
            return serializer.data
        return obj.json(dict=True)

    class Meta:
        model = Topology
        fields = (
            'label',
            'organization',
            'parser',
            'strategy',
            'key',
            'expiration_time',
            'url',
            'published',
        )
        list_serializer_class = NetworkCollectionSerializer
        extra_kwargs = {'published': {'initial': True}}


def get_representation_data(obj, dict=False, omit_down=False, **kwargs):
    """ returns a dict that represents a NetJSON NetworkGraph object """
    nodes = []
    links = []
    links_queryset = obj.get_links_queryset()
    # needed to detect links coming back online
    if omit_down:
        links_queryset = links_queryset.filter(status='up')
    # populate graph
    for link in links_queryset:
        links.append(link.json(dict=True, original=False))
    for node in obj.get_nodes_queryset():
        nodes.append(node.json(dict=True, original=False))
    netjson = OrderedDict(
        (
            ('type', 'NetworkGraph'),
            ('protocol', obj.protocol),
            ('version', obj.version),
            ('metric', obj.metric),
            ('label', obj.label),
            ('id', str(obj.id)),
            ('parser', obj.parser),
            ('organization', str(obj.organization.id)),
            ('strategy', obj.strategy),
            ('url', obj.url),
            ('key', obj.key),
            ('expiration_time', obj.expiration_time),
            ('published', obj.published),
            ('created', obj.created),
            ('modified', obj.modified),
            ('nodes', nodes),
            ('links', links),
        )
    )
    if dict:
        return netjson
    return json.dumps(netjson, cls=JSONEncoder, **kwargs)


class NetworkGraphUpdateSerializer(ValidatedModelSerializer):
    def to_representation(self, obj):
        topo_data = get_representation_data(obj, dict=True)
        if obj.strategy == 'receive':
            del topo_data['url']
        if obj.strategy == 'fetch':
            del topo_data['key']
            del topo_data['expiration_time']
        return topo_data

    class Meta:
        model = Topology
        fields = (
            'label',
            'organization',
            'parser',
            'strategy',
            'key',
            'expiration_time',
            'url',
            'published',
        )

    def validate_strategy(self, value):
        if value == 'receive' and not self.initial_data.get('key'):
            raise serializers.ValidationError(
                _('a key must be specified when using RECEIVE strategy')
            )
        return value

    def validate_url(self, value):
        if not value and self.initial_data.get('strategy') == 'fetch':
            raise serializers.ValidationError(
                _('an url must be specified when using FETCH strategy')
            )
        return value


class NodeSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    addresses = serializers.JSONField(initial=[])
    properties = serializers.JSONField(initial={})
    user_properties = serializers.JSONField(initial={})

    class Meta:
        model = Node
        fields = (
            'id',
            'topology',
            'label',
            'addresses',
            'properties',
            'user_properties',
            'created',
            'modified',
        )
        read_only_fields = ('created', 'modified')

    def validate(self, data):
        instance = self.instance or self.Meta.model(**data)
        instance.full_clean()
        data['organization'] = data.get('organization', instance.organization)
        return data


class LinkSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    properties = serializers.JSONField(initial={})
    user_properties = serializers.JSONField(
        initial={},
        help_text=_('If you need to add additional data to this link use this field'),
    )

    class Meta:
        model = Link
        fields = (
            'id',
            'topology',
            'status',
            'source',
            'target',
            'cost',
            'cost_text',
            'properties',
            'user_properties',
            'created',
            'modified',
        )
        read_only_fields = ('created', 'modified')

    def validate(self, data):
        instance = self.instance or self.Meta.model(**data)
        instance.full_clean()
        data['organization'] = data.get('organization', instance.organization)
        return data
