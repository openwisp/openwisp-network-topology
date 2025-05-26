import swapper
from django.utils.translation import gettext_lazy as _

Node = swapper.load_model("topology", "Node")
Link = swapper.load_model("topology", "Link")
Topology = swapper.load_model("topology", "Topology")


def get_name(self):
    if hasattr(self, "devicenode"):
        return self.devicenode.device.name
    return super(Node, self).get_name()


def node_get_organization_id(self):
    if hasattr(self, "devicenode"):
        return self.devicenode.device.organization_id
    return super(Node, self).get_organization_id()


def topology_get_nodes_queryset(self):
    """
    Overrides Topology.get_nodes_queryset
    to avoid generating 2 additional queries for each node
    when using the name of the device as the node label
    """
    return (
        super(Topology, self)
        .get_nodes_queryset()
        .select_related("devicenode__device")
        .only(
            "id",
            "topology_id",
            "label",
            "addresses",
            "properties",
            "user_properties",
            "created",
            "modified",
            "devicenode__device__id",
            "devicenode__device__name",
            "devicenode__device__last_ip",
            "devicenode__device__management_ip",
        )
    )


@classmethod
def node_get_queryset(cls, qs):
    return (
        super(Node, cls)
        .get_queryset(qs)
        .select_related("devicenode__device")
        .only(
            "id",
            "topology_id",
            "topology__label",
            "topology__parser",
            "organization__id",
            "organization__name",
            "organization__is_active",
            "label",
            "addresses",
            "properties",
            "user_properties",
            "devicenode__device__id",
            "devicenode__device__name",
            "devicenode__device__name",
            "devicenode__device__last_ip",
            "devicenode__device__management_ip",
        )
    )


@classmethod
def link_get_queryset(cls, qs):
    return (
        super(Link, cls)
        .get_queryset(qs)
        .select_related("source__devicenode__device", "target__devicenode__device")
        .only(
            "id",
            "topology_id",
            "topology__label",
            "topology__parser",
            "organization__id",
            "organization__name",
            "organization__is_active",
            "status",
            "properties",
            "user_properties",
            "cost",
            "cost_text",
            "source__addresses",
            "source__label",
            "source__devicenode__device__id",
            "source__devicenode__device__name",
            "source__devicenode__device__last_ip",
            "source__devicenode__device__management_ip",
            "target__addresses",
            "target__label",
            "target__devicenode__device__id",
            "target__devicenode__device__name",
            "target__devicenode__device__last_ip",
            "target__devicenode__device__management_ip",
        )
    )


Node.get_name = get_name
Node.get_name.short_description = _("label")
Node.get_organization_id = node_get_organization_id
Node.get_queryset = node_get_queryset
Link.get_queryset = link_get_queryset
Topology.get_nodes_queryset = topology_get_nodes_queryset
