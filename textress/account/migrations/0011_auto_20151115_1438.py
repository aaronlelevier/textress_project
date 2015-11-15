# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20151115_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricing',
            name='hotel',
            field=models.OneToOneField(related_name='pricing', default=1, to='main.Hotel'),
            preserve_default=False,
        ),
    ]
