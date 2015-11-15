# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20151113_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(default=None, help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True),
        ),
    ]
