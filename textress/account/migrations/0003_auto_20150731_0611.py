# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20150728_0602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctcost',
            name='auto_recharge',
            field=models.BooleanField(default=True, verbose_name=b'Auto Recharge On'),
        ),
    ]
