# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitcollector', '0004_auto_20161223_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='docker_id',
            field=models.TextField(default=2),
            preserve_default=False,
        ),
    ]
