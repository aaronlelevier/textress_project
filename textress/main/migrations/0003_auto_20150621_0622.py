# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_hotel_group_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='address_zip',
            field=models.PositiveIntegerField(help_text=b'5-digit zipcode. i.e.: 89109', verbose_name='Zipcode'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='rooms',
            field=models.IntegerField(null=True, verbose_name='Rooms', blank=True),
        ),
    ]
