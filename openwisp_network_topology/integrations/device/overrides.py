import swapper

Node = swapper.load_model('topology', 'Node')
Link = swapper.load_model('topology', 'Link')
Topology = swapper.load_model('topology', 'Topology')


def get_name(self):
    if hasattr(self, 'devicenode'):
        return self.devicenode.device.name
    return super(Node, self).get_name()


def topology_get_nodes_queryset(self):
    """
    Overrides Topology.get_nodes_queryset
    to avoid generating 2 additional queries for each node
    when using the name of the device as the node label
    """
    return (
        super(Topology, self)
        .get_nodes_queryset()
        .select_related('devicenode__device')
        .only(
            'id',
            'topology_id',
            'label',
            'addresses',
            'properties',
            'user_properties',
            'created',
            'modified',
            'devicenode__device__name',
        )
    )


@classmethod
def node_get_queryset(cls, qs):
    return (
        super(Node, cls)
        .get_queryset(qs)
        .select_related('devicenode__device')
        .only(
            'id',
            'topology_id',
            'topology__label',
            'topology__parser',
            'organization__id',
            'organization__name',
            'organization__is_active',
            'label',
            'addresses',
            'devicenode__device__name',
        )
    )


@classmethod
def link_get_queryset(cls, qs):
    return (
        super(Link, cls)
        .get_queryset(qs)
        .select_related('source__devicenode__device', 'target__devicenode__device')
        .only(
            'id',
            'topology_id',
            'topology__label',
            'topology__parser',
            'organization__id',
            'organization__name',
            'organization__is_active',
            'status',
            'cost',
            'cost_text',
            'source__addresses',
            'source__label',
            'source__devicenode__device__name',
            'target__addresses',
            'target__label',
            'target__devicenode__device__name',
        )
    )


Node.get_name = get_name
Node.get_queryset = node_get_queryset
Link.get_queryset = link_get_queryset
Topology.get_nodes_queryset = topology_get_nodes_queryset
