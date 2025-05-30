# Generated by Django 4.0.1 on 2022-01-31 18:06

import django.db.models.deletion
from django.db import migrations, models
from swapper import get_model_name


class Migration(migrations.Migration):
    dependencies = [
        ("topology", "0014_remove_snapshot_organization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=get_model_name("openwisp_users", "Organization"),
                verbose_name="organization",
            ),
        ),
        migrations.AlterField(
            model_name="node",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=get_model_name("openwisp_users", "Organization"),
                verbose_name="organization",
            ),
        ),
        migrations.AlterField(
            model_name="topology",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=get_model_name("openwisp_users", "Organization"),
                verbose_name="organization",
            ),
        ),
    ]
