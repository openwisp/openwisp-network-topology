# Generated by Django 3.0.9 on 2020-09-01 14:57

import collections

import jsonfield.fields
import rest_framework.utils.encoders
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("topology", "0012_update_openvpn_netjson_ids")]

    operations = [
        migrations.AddField(
            model_name="link",
            name="user_properties",
            field=jsonfield.fields.JSONField(
                blank=True,
                default=dict,
                dump_kwargs={
                    "cls": rest_framework.utils.encoders.JSONEncoder,
                    "indent": 4,
                },
                help_text="If you need to add additional data to this link use this field",
                load_kwargs={"object_pairs_hook": collections.OrderedDict},
                verbose_name="user defined properties",
            ),
        ),
        migrations.AddField(
            model_name="node",
            name="user_properties",
            field=jsonfield.fields.JSONField(
                blank=True,
                default=dict,
                dump_kwargs={
                    "cls": rest_framework.utils.encoders.JSONEncoder,
                    "indent": 4,
                },
                help_text="If you need to add additional data to this node use this field",
                load_kwargs={"object_pairs_hook": collections.OrderedDict},
                verbose_name="user defined properties",
            ),
        ),
    ]
