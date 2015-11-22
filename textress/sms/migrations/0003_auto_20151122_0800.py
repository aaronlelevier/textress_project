# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_auto_20151019_0642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='hotel',
            field=models.ForeignKey(related_name='phone_numbers', to='main.Hotel'),
        ),
    ]
