import swapper


def get_model(apps, app_name, model):
    model_name = swapper.get_model_name(app_name, model)
    model_label = swapper.split(model_name)[0]
    return apps.get_model(model_label, model)


def create_relations_0001(apps, schema_editor):
    Node = get_model(apps, 'topology', 'Node')
    DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
    queryset = Node.objects.select_related('topology').filter(
        topology__parser='netdiff.OpenvpnParser'
    )
    for node in queryset.iterator():
        DeviceNode.auto_create(node)
