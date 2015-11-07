# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20151107_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(help_text=b'Current blance, just like in a Bank Account.', null=True, verbose_name='Balance', blank=True),
        ),
    ]
