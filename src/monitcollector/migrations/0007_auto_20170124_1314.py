# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitcollector', '0006_auto_20170122_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='date',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='container',
            name='date_last',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
