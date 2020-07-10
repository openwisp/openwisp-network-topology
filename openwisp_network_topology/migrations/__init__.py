# Manually written, used during migrations


def migrate_addresses(apps, schema_editor, app='topology'):
    Node = apps.get_model(app, 'Node')
    for node in Node.objects.iterator():
        addresses = node.addresses_old.replace(' ', '')
        if addresses.startswith(';'):
            addresses = addresses[1:]
        addresses = addresses[0:-1].split(';')
        node.addresses = addresses
        node.save()
