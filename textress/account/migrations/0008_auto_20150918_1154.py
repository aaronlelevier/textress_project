# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20150912_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricing',
            name='price',
            field=models.DecimalField(help_text=b"Price in $'s. Ex: 0.0525", verbose_name='Price per SMS', max_digits=3, decimal_places=2),
        ),
    ]
