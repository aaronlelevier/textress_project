# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0009_auto_20151019_0724'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='hidden',
        ),
        migrations.RemoveField(
            model_name='trigger',
            name='hidden',
        ),
        migrations.RemoveField(
            model_name='triggertype',
            name='hidden',
        ),
        migrations.AlterField(
            model_name='guest',
            name='phone_number',
            field=models.CharField(help_text=b'Allowed phone number format: (702) 510-5555', max_length=12, verbose_name='Phone Number'),
        ),
    ]
