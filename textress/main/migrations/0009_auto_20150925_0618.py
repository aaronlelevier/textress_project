# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150829_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='address_phone',
            field=models.CharField(help_text=b'Allowed phone number format: 702-510-5555', unique=True, max_length=12, verbose_name='Contact Phone Number'),
        ),
    ]
