from django.db import migrations
import swapper


def fix_link_properties(apps, schema_editor):
    Link = swapper.load_model('topology', 'Link')
    for link in Link.objects.all():
        link.full_clean()
        link.save()


class Migration(migrations.Migration):
    dependencies = [
        ('topology', '0010_properties_json'),
    ]

    operations = [
        migrations.RunPython(
            fix_link_properties, reverse_code=migrations.RunPython.noop
        )
    ]
