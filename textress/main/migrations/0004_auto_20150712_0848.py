# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150711_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='twilio_phone_number',
            field=models.CharField(max_length=25, null=True, verbose_name='Twilio Phone Number', blank=True),
        ),
    ]
