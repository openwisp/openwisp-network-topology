# Manually written, used during migrations
import swapper


def migrate_addresses(apps, schema_editor, app='topology'):
    Node = apps.get_model(app, 'Node')
    for node in Node.objects.iterator():
        addresses = node.addresses_old.replace(' ', '')
        if addresses.startswith(';'):
            addresses = addresses[1:]
        addresses = addresses[0:-1].split(';')
        node.addresses = addresses
        node.save()


def migrate_openvpn_ids_0012(apps, schema_editor, app='topology'):
    Node = swapper.load_model('topology', 'Node')
    queryset = Node.objects.filter(topology__parser='netdiff.OpenvpnParser')
    for node in queryset.iterator():
        node.addresses[0] = node.label
        node.full_clean()
        node.save()
