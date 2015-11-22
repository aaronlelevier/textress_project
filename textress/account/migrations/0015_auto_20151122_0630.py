# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20151116_0607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctstmt',
            name='balance',
            field=models.IntegerField(default=0, help_text=b'Monthly Cost + (SMS Used * Cost Per SMS)', verbose_name='Current Funds Balance', blank=True),
        ),
    ]
