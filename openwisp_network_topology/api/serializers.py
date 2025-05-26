from collections import OrderedDict

import swapper
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from openwisp_users.api.mixins import FilterSerializerByOrgManaged
from openwisp_utils.api.serializers import ValidatedModelSerializer

Node = swapper.load_model("topology", "Node")
Link = swapper.load_model("topology", "Link")
Topology = swapper.load_model("topology", "Topology")


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
                ("type", "NetworkCollection"),
                ("collection", super().to_representation(data)),
            )
        )


def get_receive_url(pk, key):
    path = reverse("receive_topology", args=[pk])
    url = "{0}?key={1}".format(path, key)
    return url


def get_representation_data(obj):
    """
    Returns a dict that represents
    a NetJSON NetworkGraph object.
    """
    nodes = []
    links = []
    for link in obj.get_links_queryset():
        links.append(link.json(dict=True, original=False))
    for node in obj.get_nodes_queryset():
        nodes.append(node.json(dict=True, original=False))
    netjson = OrderedDict(
        (
            ("type", "NetworkGraph"),
            ("protocol", obj.protocol),
            ("version", obj.version),
            ("metric", obj.metric),
            ("label", obj.label),
            ("id", str(obj.id)),
            ("parser", obj.parser),
            ("organization", str(obj.organization.id) if obj.organization else None),
            ("strategy", obj.strategy),
            ("url", obj.url),
            ("key", obj.key),
            ("expiration_time", obj.expiration_time),
            ("receive_url", get_receive_url(obj.pk, obj.key)),
            ("published", obj.published),
            ("created", obj.created),
            ("modified", obj.modified),
            ("nodes", nodes),
            ("links", links),
        )
    )
    return netjson


class NetworkGraphRepresentation(object):
    def to_representation(self, obj):
        """
        Overriding the default represenation
        of Topology object.
        """
        topology_data = get_representation_data(obj)
        topology_data["receive_url"] = self.context["request"].build_absolute_uri(
            topology_data["receive_url"]
        )
        return topology_data


class TopologySerializer(NetworkGraphRepresentation, ValidatedModelSerializer):
    class Meta:
        model = Topology
        fields = "__all__"


class BaseSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    pass


class NetworkGraphSerializer(BaseSerializer):
    """
    NetJSON NetworkGraph.
    """

    def to_representation(self, obj):
        if self.context["request"].method == "POST":
            serializer = TopologySerializer(
                self.instance, context={"request": self.context["request"]}
            )
            return serializer.data
        return obj.json(dict=True)

    class Meta:
        model = Topology
        fields = (
            "label",
            "organization",
            "parser",
            "strategy",
            "key",
            "expiration_time",
            "url",
            "published",
        )
        list_serializer_class = NetworkCollectionSerializer
        extra_kwargs = {"published": {"initial": True}}


class NetworkGraphUpdateSerializer(NetworkGraphRepresentation, BaseSerializer):
    class Meta:
        model = Topology
        fields = (
            "label",
            "organization",
            "parser",
            "strategy",
            "key",
            "expiration_time",
            "url",
            "published",
        )

    def validate_strategy(self, value):
        if value == "receive" and not self.initial_data.get("key"):
            raise serializers.ValidationError(
                _("A key must be specified when using RECEIVE strategy")
            )
        return value

    def validate_url(self, value):
        if not value and self.initial_data.get("strategy") == "fetch":
            raise serializers.ValidationError(
                _("An url must be specified when using FETCH strategy")
            )
        return value


class BaseNodeLinkSerializer(BaseSerializer):
    properties = serializers.JSONField(initial={})

    def validate(self, data):
        instance = self.instance or self.Meta.model(**data)
        instance.full_clean()
        data["organization"] = instance.organization
        return data

    def validate_properties(self, value):
        if type(value) is not dict:
            raise serializers.ValidationError(
                _("Value must be valid JSON or key, valued pair.")
            )
        return value

    def validate_user_properties(self, value):
        if type(value) is not dict:
            raise serializers.ValidationError(
                _("Value must be valid JSON or key, valued pair.")
            )
        return value


class NodeSerializer(BaseNodeLinkSerializer):
    addresses = serializers.JSONField(initial=[])
    user_properties = serializers.JSONField(initial={})

    class Meta:
        model = Node
        fields = (
            "id",
            "topology",
            "organization",
            "label",
            "addresses",
            "properties",
            "user_properties",
            "created",
            "modified",
        )
        read_only_fields = ("created", "modified")


class LinkSerializer(BaseNodeLinkSerializer):
    user_properties = serializers.JSONField(
        initial={},
        help_text=_("If you need to add additional data to this link use this field"),
    )

    class Meta:
        model = Link
        fields = (
            "id",
            "topology",
            "organization",
            "status",
            "source",
            "target",
            "cost",
            "cost_text",
            "properties",
            "user_properties",
            "created",
            "modified",
        )
        read_only_fields = ("organization", "created", "modified")
