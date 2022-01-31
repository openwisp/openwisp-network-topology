# Generated by Django 4.0.1 on 2022-01-31 18:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_users', '0017_user_language'),
        ('topology', '0013_add_user_defined_properties_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='openwisp_users.organization',
                verbose_name='organization',
            ),
        ),
        migrations.AlterField(
            model_name='node',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='openwisp_users.organization',
                verbose_name='organization',
            ),
        ),
        migrations.AlterField(
            model_name='topology',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='openwisp_users.organization',
                verbose_name='organization',
            ),
        ),
    ]
