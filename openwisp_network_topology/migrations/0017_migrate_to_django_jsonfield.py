# Generated migration to replace third-party JSONField with Django built-in JSONField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topology', '0016_alter_topology_parser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='properties',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='link',
            name='user_properties',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='If you need to add additional data to this link use this field',
                verbose_name='user defined properties'
            ),
        ),
        migrations.AlterField(
            model_name='node',
            name='addresses',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='node',
            name='properties',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='node',
            name='user_properties',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='If you need to add additional data to this node use this field',
                verbose_name='user defined properties'
            ),
        ),
    ]
