# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitcollector', '0005_container_docker_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='image',
            field=models.TextField(default='asddf'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='container',
            name='state',
            field=models.TextField(default='asdf'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='container',
            name='status',
            field=models.TextField(default='asddf'),
            preserve_default=False,
        ),
    ]
