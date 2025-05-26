from swapper import load_model

from openwisp_users.api.filters import OrganizationManagedFilter

Node = load_model("topology", "Node")
Link = load_model("topology", "Link")
Topology = load_model("topology", "Topology")


class NetworkCollectionFilter(OrganizationManagedFilter):
    class Meta(OrganizationManagedFilter.Meta):
        model = Topology
        fields = OrganizationManagedFilter.Meta.fields + ["strategy", "parser"]


class NodeFilter(OrganizationManagedFilter):
    class Meta(OrganizationManagedFilter.Meta):
        model = Node
        fields = OrganizationManagedFilter.Meta.fields + ["topology"]


class LinkFilter(OrganizationManagedFilter):
    class Meta(OrganizationManagedFilter.Meta):
        model = Link
        fields = OrganizationManagedFilter.Meta.fields + ["topology", "status"]
