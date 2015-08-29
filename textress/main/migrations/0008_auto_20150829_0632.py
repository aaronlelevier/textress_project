# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150829_0629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icon',
            name='name',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
    ]
