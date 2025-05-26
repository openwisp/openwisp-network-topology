from django.db import migrations

from . import fix_link_properties


class Migration(migrations.Migration):
    dependencies = [("topology", "0010_properties_json")]

    operations = [
        migrations.RunPython(
            fix_link_properties, reverse_code=migrations.RunPython.noop
        )
    ]
