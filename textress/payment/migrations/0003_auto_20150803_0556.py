# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20150803_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardimage',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
