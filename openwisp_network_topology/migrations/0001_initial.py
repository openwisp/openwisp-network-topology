# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 13:31

import collections
import re
import uuid

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
from django.db import migrations, models

import openwisp_utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [('openwisp_users', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('cost', models.FloatField()),
                ('cost_text', models.CharField(blank=True, max_length=24)),
                (
                    'status',
                    model_utils.fields.StatusField(
                        choices=[('up', 'up'), ('down', 'down')],
                        default='up',
                        max_length=100,
                        no_check_for_status=True,
                    ),
                ),
                (
                    'properties',
                    jsonfield.fields.JSONField(
                        blank=True,
                        default=dict,
                        dump_kwargs={'indent': 4},
                        load_kwargs={'object_pairs_hook': collections.OrderedDict},
                    ),
                ),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='openwisp_users.Organization',
                        verbose_name='organization',
                    ),
                ),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('label', models.CharField(blank=True, max_length=64)),
                ('addresses', models.CharField(db_index=True, max_length=510)),
                (
                    'properties',
                    jsonfield.fields.JSONField(
                        blank=True,
                        default=dict,
                        dump_kwargs={'indent': 4},
                        load_kwargs={'object_pairs_hook': collections.OrderedDict},
                    ),
                ),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='openwisp_users.Organization',
                        verbose_name='organization',
                    ),
                ),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='Topology',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('label', models.CharField(max_length=64, verbose_name='label')),
                (
                    'parser',
                    models.CharField(
                        choices=[
                            ('netdiff.OlsrParser', 'OLSRd (txtinfo/jsoninfo)'),
                            (
                                'netdiff.BatmanParser',
                                'batman-advanced (jsondoc/txtinfo)',
                            ),
                            ('netdiff.BmxParser', 'BMX6 (q6m)'),
                            ('netdiff.NetJsonParser', 'NetJSON NetworkGraph'),
                            ('netdiff.CnmlParser', 'CNML 1.0'),
                        ],
                        help_text='Select topology format',
                        max_length=128,
                        verbose_name='format',
                    ),
                ),
                (
                    'strategy',
                    models.CharField(
                        choices=[('fetch', 'FETCH'), ('receive', 'RECEIVE')],
                        db_index=True,
                        default='fetch',
                        max_length=16,
                        verbose_name='strategy',
                    ),
                ),
                (
                    'url',
                    models.URLField(
                        blank=True,
                        help_text='Topology data will be fetched from this URL (FETCH strategy)',
                        verbose_name='url',
                    ),
                ),
                (
                    'key',
                    openwisp_utils.base.KeyField(
                        blank=True,
                        default=openwisp_utils.utils.get_random_key,
                        help_text='key needed to update topology from nodes ',
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile('^[^\\s/\\.]+$'),
                                code='invalid',
                                message='This value must not contain spaces, dots or slashes.',
                            )
                        ],
                        verbose_name='key',
                    ),
                ),
                (
                    'expiration_time',
                    models.PositiveIntegerField(
                        default=0,
                        help_text=(
                            '"Expiration Time" in seconds: setting this to 0 will '
                            'immediately mark missing links as down; a value higher '
                            'than 0 will delay marking missing links as down until '
                            'the "modified" field of a link is older than "Expiration Time"'
                        ),
                        verbose_name='expiration time',
                    ),
                ),
                (
                    'published',
                    models.BooleanField(
                        default=True,
                        help_text="Unpublished topologies won't be updated or shown in the visualizer",
                        verbose_name='published',
                    ),
                ),
                (
                    'protocol',
                    models.CharField(
                        blank=True, max_length=64, verbose_name='protocol'
                    ),
                ),
                (
                    'version',
                    models.CharField(blank=True, max_length=24, verbose_name='version'),
                ),
                (
                    'revision',
                    models.CharField(
                        blank=True, max_length=64, verbose_name='revision'
                    ),
                ),
                (
                    'metric',
                    models.CharField(blank=True, max_length=24, verbose_name='metric'),
                ),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='openwisp_users.Organization',
                        verbose_name='organization',
                    ),
                ),
            ],
            options={'verbose_name_plural': 'topologies', 'abstract': False},
        ),
        migrations.AddField(
            model_name='node',
            name='topology',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='topology.Topology'
            ),
        ),
        migrations.AddField(
            model_name='link',
            name='source',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='source_link_set',
                to='topology.Node',
            ),
        ),
        migrations.AddField(
            model_name='link',
            name='target',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='source_target_set',
                to='topology.Node',
            ),
        ),
        migrations.AddField(
            model_name='link',
            name='topology',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='topology.Topology'
            ),
        ),
    ]
