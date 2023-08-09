# Generated by Django 4.0.5 on 2022-06-01 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topology', '0015_shareable_topology_node_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topology',
            name='parser',
            field=models.CharField(
                choices=[
                    ('netdiff.OlsrParser', 'OLSRd (txtinfo/jsoninfo)'),
                    ('netdiff.BatmanParser', 'batman-advanced (jsondoc/txtinfo)'),
                    ('netdiff.BmxParser', 'BMX6 (q6m)'),
                    ('netdiff.NetJsonParser', 'NetJSON NetworkGraph'),
                    ('netdiff.CnmlParser', 'CNML 1.0'),
                    ('netdiff.OpenvpnParser', 'OpenVPN'),
                    ('netdiff.WireguardParser', 'Wireguard'),
                    ('netdiff.ZeroTierParser', 'ZeroTier'),
                ],
                help_text='Select topology format',
                max_length=128,
                verbose_name='format',
            ),
        ),
    ]
