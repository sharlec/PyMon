# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.TextField(null=True)),
                ('release', models.TextField(null=True)),
                ('version', models.TextField(null=True)),
                ('machine', models.TextField(null=True)),
                ('cpu', models.IntegerField(null=True)),
                ('memory', models.IntegerField(null=True)),
                ('swap', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('monit_id', models.CharField(max_length=32, unique=True)),
                ('monit_version', models.TextField(null=True)),
                ('localhostname', models.TextField(null=True)),
                ('uptime', models.IntegerField(null=True)),
                ('address', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('status', models.TextField(null=True)),
                ('status_hint', models.IntegerField(null=True)),
                ('monitor', models.IntegerField(null=True)),
                ('monitormode', models.IntegerField(null=True)),
                ('pendingaction', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('service_ptr', models.OneToOneField(auto_created=True, serialize=False, to='monitcollector.Service', parent_link=True, primary_key=True)),
                ('state', models.IntegerField(null=True)),
                ('speed', models.IntegerField(null=True)),
                ('duplex', models.IntegerField(null=True)),
                ('download_packets_now', models.IntegerField(null=True)),
                ('download_packets_total', models.IntegerField(null=True)),
                ('download_bytes_now', models.IntegerField(null=True)),
                ('download_bytes_total', models.IntegerField(null=True)),
                ('download_errors_now', models.IntegerField(null=True)),
                ('download_errors_total', models.IntegerField(null=True)),
                ('upload_packets_now', models.IntegerField(null=True)),
                ('upload_packets_total', models.IntegerField(null=True)),
                ('upload_bytes_now', models.IntegerField(null=True)),
                ('upload_bytes_total', models.IntegerField(null=True)),
                ('upload_errors_now', models.IntegerField(null=True)),
                ('upload_errors_total', models.IntegerField(null=True)),
                ('server', models.ForeignKey(to='monitcollector.Server')),
            ],
            bases=('monitcollector.service',),
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('service_ptr', models.OneToOneField(auto_created=True, serialize=False, to='monitcollector.Service', parent_link=True, primary_key=True)),
                ('date_last', models.PositiveIntegerField(null=True)),
                ('date', models.TextField(null=True)),
                ('pid', models.IntegerField(null=True)),
                ('ppid', models.IntegerField(null=True)),
                ('uptime', models.PositiveIntegerField(null=True)),
                ('children', models.PositiveIntegerField(null=True)),
                ('cpu_percenttotal_last', models.FloatField(null=True)),
                ('cpu_percenttotal', models.TextField(null=True)),
                ('memory_percenttotal_last', models.FloatField(null=True)),
                ('memory_percenttotal', models.TextField(null=True)),
                ('memory_kilobytetotal_last', models.PositiveIntegerField(null=True)),
                ('memory_kilobytetotal', models.TextField(null=True)),
                ('server', models.ForeignKey(to='monitcollector.Server')),
            ],
            bases=('monitcollector.service',),
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('service_ptr', models.OneToOneField(auto_created=True, serialize=False, to='monitcollector.Service', parent_link=True, primary_key=True)),
                ('date_last', models.PositiveIntegerField(null=True)),
                ('date', models.TextField(null=True)),
                ('load_avg01_last', models.FloatField(null=True)),
                ('load_avg01', models.TextField(null=True)),
                ('load_avg05_last', models.FloatField(null=True)),
                ('load_avg05', models.TextField(null=True)),
                ('load_avg15_last', models.FloatField(null=True)),
                ('load_avg15', models.TextField(null=True)),
                ('cpu_user_last', models.FloatField(null=True)),
                ('cpu_user', models.TextField(null=True)),
                ('cpu_system_last', models.FloatField(null=True)),
                ('cpu_system', models.TextField(null=True)),
                ('cpu_wait_last', models.FloatField(null=True)),
                ('cpu_wait', models.TextField(null=True)),
                ('memory_percent_last', models.FloatField(null=True)),
                ('memory_percent', models.TextField(null=True)),
                ('memory_kilobyte_last', models.PositiveIntegerField(null=True)),
                ('memory_kilobyte', models.TextField(null=True)),
                ('swap_percent_last', models.FloatField(null=True)),
                ('swap_percent', models.TextField(null=True)),
                ('swap_kilobyte_last', models.PositiveIntegerField(null=True)),
                ('swap_kilobyte', models.TextField(null=True)),
                ('server', models.OneToOneField(to='monitcollector.Server')),
            ],
            bases=('monitcollector.service',),
        ),
        migrations.AddField(
            model_name='platform',
            name='server',
            field=models.OneToOneField(to='monitcollector.Server'),
        ),
    ]
