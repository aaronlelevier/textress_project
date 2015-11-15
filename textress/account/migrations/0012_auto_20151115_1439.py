# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20151115_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricing',
            name='hotel',
            field=models.OneToOneField(related_name='pricing', null=True, blank=True, to='main.Hotel'),
        ),
    ]
