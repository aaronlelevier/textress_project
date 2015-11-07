# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20151107_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(default=0, help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True),
        ),
    ]
