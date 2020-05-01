from collections import OrderedDict

import swapper
from rest_framework import serializers


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


class NetworkGraphSerializer(serializers.ModelSerializer):
    """
    NetJSON NetworkGraph
    """

    def to_representation(self, obj):
        return obj.json(dict=True)

    class Meta:
        model = swapper.load_model('topology', 'Topology')
        fields = '__all__'
        list_serializer_class = NetworkCollectionSerializer
