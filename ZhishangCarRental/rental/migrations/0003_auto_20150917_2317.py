# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0002_auto_20150821_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='violation',
            name='kind',
            field=models.CharField(max_length=30),
        ),
    ]
