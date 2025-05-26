from django.db import migrations

from . import migrate_openvpn_ids_0012


class Migration(migrations.Migration):
    dependencies = [("topology", "0011_fix_link_properties")]

    operations = [
        migrations.RunPython(
            migrate_openvpn_ids_0012, reverse_code=migrations.RunPython.noop
        )
    ]
