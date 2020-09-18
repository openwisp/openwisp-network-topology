from django.db import migrations

from . import create_relations_0001


class Migration(migrations.Migration):
    dependencies = [
        ('topology_device', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_relations_0001, reverse_code=migrations.RunPython.noop
        )
    ]
