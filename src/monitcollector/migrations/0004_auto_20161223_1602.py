# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitcollector', '0003_container'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='cpu_last',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='container',
            name='memory_last',
            field=models.FloatField(null=True),
        ),
    ]
