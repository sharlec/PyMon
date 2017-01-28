# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitcollector', '0002_auto_20161207_1959'),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('cpu_last', models.IntegerField(null=True)),
                ('cpu', models.TextField(null=True)),
                ('memory_last', models.IntegerField(null=True)),
                ('memory', models.TextField(null=True)),
                ('process', models.ForeignKey(to='monitcollector.Process')),
            ],
        ),
    ]
