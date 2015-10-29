# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='address_phone',
            field=models.CharField(help_text=b'Allowed phone number format: (702) 510-5555', unique=True, max_length=12, verbose_name='Contact Phone Number'),
        ),
    ]
