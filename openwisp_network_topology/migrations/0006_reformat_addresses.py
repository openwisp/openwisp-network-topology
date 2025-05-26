from django.db import migrations


def reformat_address_forward(apps, schema_editor):
    Node = apps.get_model("topology", "Node")
    for node in Node.objects.all():
        if not node.addresses.startswith(";"):
            node.addresses = ";{0}".format(node.addresses)
            node.save()


def reformat_address_backward(apps, schema_editor):
    Fake_node_model = apps.get_model("topology", "Node")
    for node in Fake_node_model.objects.all():
        if node.addresses.startswith(";"):
            node.addresses = node.addresses[1:]
            node.save()


class Migration(migrations.Migration):
    dependencies = [("topology", "0005_default_operator_permission")]

    operations = [
        migrations.RunPython(reformat_address_forward, reformat_address_backward)
    ]
