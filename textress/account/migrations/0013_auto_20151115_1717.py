# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20151115_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(help_text=b'Current blance, just like in a Bank Account.', null=True, verbose_name='Balance', blank=True),
        ),
    ]
