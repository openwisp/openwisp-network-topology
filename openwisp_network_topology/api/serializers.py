from collections import OrderedDict

import swapper
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from openwisp_users.api.mixins import FilterSerializerByOrgManaged
from openwisp_utils.api.serializers import ValidatedModelSerializer

Node = swapper.load_model('topology', 'Node')
Link = swapper.load_model('topology', 'Link')


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


class NetworkGraphSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    """
    NetJSON NetworkGraph
    """

    def to_representation(self, obj):
        return obj.json(dict=True)

    class Meta:
        model = swapper.load_model('topology', 'Topology')
        fields = (
            'label',
            'organization',
            'parser',
            'strategy',
            'key',
            'expiration_time',
            'url',
            'published',
            'protocol',
            'version',
            'revision',
            'metric',
        )
        list_serializer_class = NetworkCollectionSerializer
        extra_kwargs = {
            'protocol': {'read_only': True},
            'version': {'read_only': True},
            'revision': {'read_only': True},
            'metric': {'read_only': True},
        }


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
