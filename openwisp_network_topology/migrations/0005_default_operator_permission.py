from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import migrations
from swapper import dependency, split

from . import create_default_permissions


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

    operators_can_manage = ["link", "node"]
    operators_can_only_view = ["topology"]
    admin_can_manage = ["link", "node", "topology"]
    manage_operations = ["add", "change", "delete", "view"]
    view_only_operations = ["view"]
    Group = apps.get_model("openwisp_users", "Group")

    try:
        admin = Group.objects.get(name="Administrator")
        operator = Group.objects.get(name="Operator")
    # consider failures custom cases
    # that do not have to be dealt with
    except Group.DoesNotExist:
        return

    # Add permissions for operators
    _add_permission_to_group(operator, operators_can_manage, manage_operations)
    _add_permission_to_group(operator, operators_can_only_view, view_only_operations)
    # Add permissions for Administrator
    _add_permission_to_group(admin, admin_can_manage, manage_operations)


class Migration(migrations.Migration):
    dependencies = [
        dependency(*split(settings.AUTH_USER_MODEL), version="0004_default_groups"),
        ("topology", "0004_fixed_target_link_set"),
    ]
    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        )
    ]
