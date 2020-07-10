from django.db import migrations

import swapper


def create_relations_0001(apps, schema_editor, app='topology'):
    Node = swapper.load_model('topology', 'Node')
    DeviceNode = swapper.load_model('topology_device', 'DeviceNode')
    queryset = Node.objects.select_related('topology').filter(
        topology__parser='netdiff.OpenvpnParser'
    )
    for node in queryset.iterator():
        DeviceNode.auto_create(node)


class Migration(migrations.Migration):
    dependencies = [
        ('topology_device', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_relations_0001, reverse_code=migrations.RunPython.noop
        )
    ]
