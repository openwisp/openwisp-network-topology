# Manually written, used during migrations
import json

import swapper
from django.contrib.auth.management import create_permissions


def get_model(apps, app_name, model):
    model_name = swapper.get_model_name(app_name, model)
    model_label = swapper.split(model_name)[0]
    return apps.get_model(model_label, model)


def migrate_addresses(apps, schema_editor):
    Node = get_model(apps, "topology", "Node")
    for node in Node.objects.iterator():
        addresses = node.addresses_old.replace(" ", "")
        if addresses.startswith(";"):
            addresses = addresses[1:]
        addresses = addresses[0:-1].split(";")
        node.addresses = json.dumps(addresses)
        node.save()


def migrate_openvpn_ids_0012(apps, schema_editor):
    Node = get_model(apps, "topology", "Node")
    queryset = Node.objects.filter(topology__parser="netdiff.OpenvpnParser")
    for node in queryset.iterator():
        # The historical addresses field is now TextField, so the value is
        # the raw JSON string written by jsonfield in older releases (or by
        # migrate_addresses above). Decode it before mutating.
        addresses = node.addresses
        if isinstance(addresses, str):
            addresses = json.loads(addresses)
        if not addresses:
            addresses = [node.label]
        else:
            addresses[0] = node.label
        node.addresses = json.dumps(addresses)
        node.full_clean()
        node.save()


def fix_link_properties(apps, schema_editor):
    Link = get_model(apps, "topology", "Link")
    for link in Link.objects.all():
        link.full_clean()
        link.save()


def create_default_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None
