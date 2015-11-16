# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20151115_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(default=0, help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True),
            preserve_default=False,
        ),
    ]
