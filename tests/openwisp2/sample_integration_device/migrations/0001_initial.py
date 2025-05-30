# Generated by Django 2.2.14 on 2020-07-15 21:26

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.CONFIG_DEVICE_MODEL),
        ("sample_network_topology", "0002_json_properties"),
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
                ("is_test", models.BooleanField(default=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.CONFIG_DEVICE_MODEL,
                    ),
                ),
                (
                    "node",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sample_network_topology.Node",
                    ),
                ),
            ],
            options={"abstract": False, "unique_together": {("node", "device")}},
        ),
        migrations.CreateModel(
            name="WifiMesh",
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
                ("mesh_id", models.CharField(max_length=32, verbose_name="Mesh ID")),
                ("is_test", models.BooleanField(default=True)),
                (
                    "topology",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.TOPOLOGY_TOPOLOGY_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
