from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.db import migrations


def create_default_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def assign_permissions_to_groups(apps, schema_editor):
    create_default_permissions(apps, schema_editor)
    operators_and_admin_can_change = ['link', 'node']
    operators_read_only_admins_manage = ['topology']
    manage_operations = ['add', 'change', 'delete']
    Group = apps.get_model('openwisp_users', 'Group')

    try:
        admin = Group.objects.get(name='Administrator')
        operator = Group.objects.get(name='Operator')
    # consider failures custom cases
    # that do not have to be dealt with
    except Group.DoesNotExist:
        return

    for model_name in operators_and_admin_can_change:
        for operation in manage_operations:
            permission = Permission.objects.get(
                codename='{}_{}'.format(operation, model_name)
            )
            admin.permissions.add(permission.pk)
            operator.permissions.add(permission.pk)
    for model_name in operators_read_only_admins_manage:
        try:
            permission = Permission.objects.get(codename="view_{}".format(model_name))
            operator.permissions.add(permission.pk)
        except Permission.DoesNotExist:
            pass
        for operation in manage_operations:
            admin.permissions.add(
                Permission.objects.get(
                    codename="{}_{}".format(operation, model_name)
                ).pk
            )


class Migration(migrations.Migration):
    dependencies = [
        ('openwisp_users', '0004_default_groups'),
        ('topology', '0004_fixed_target_link_set'),
    ]
    operations = [
        migrations.RunPython(
            assign_permissions_to_groups, reverse_code=migrations.RunPython.noop
        )
    ]
