from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import migrations

from openwisp_network_topology.migrations import create_default_permissions


def assign_permissions_to_groups(apps, schema_editor):
    create_default_permissions(apps, schema_editor)

    def _add_permission_to_group(group, models, operations):
        for model in models:
            for operation in operations:
                try:
                    permission = Permission.objects.get(
                        codename="{}_{}".format(operation, model)
                    )
                except Permission.DoesNotExist:
                    continue
                else:
                    group.permissions.add(permission.pk)

    Group = apps.get_model("openwisp_users", "Group")
    manage_operations = ["add", "change", "delete", "view"]
    try:
        admin = Group.objects.get(name="Administrator")
        operator = Group.objects.get(name="Operator")
    # consider failures custom cases
    # that do not have to be dealt with
    except Group.DoesNotExist:
        return

    _add_permission_to_group(operator, ["wifimesh"], manage_operations)
    _add_permission_to_group(admin, ["wifimesh"], manage_operations)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.TOPOLOGY_TOPOLOGY_MODEL),
        ("topology_device", "0002_wifimesh"),
    ]

    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        )
    ]
