# Generated by Django 2.2.14 on 2020-07-15 21:25

import uuid

import django.db.models.deletion
import swapper
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        swapper.dependency("topology", "Node"),
        swapper.dependency("config", "Device"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceNode",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=swapper.get_model_name("config", "Device"),
                    ),
                ),
                (
                    "node",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=swapper.get_model_name("topology", "Node"),
                    ),
                ),
            ],
            options={
                "abstract": False,
                "swappable": swapper.swappable_setting("topology_device", "DeviceNode"),
                "unique_together": {("node", "device")},
            },
        )
    ]
