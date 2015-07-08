# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='twilio_auth_token',
            field=models.CharField(max_length=100, null=True, verbose_name='Twilio Auth Token', blank=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='twilio_ph_sid',
            field=models.CharField(max_length=100, null=True, verbose_name='Twilio Phone Number Sid', blank=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='twilio_phone_number',
            field=models.CharField(max_length=12, null=True, verbose_name='Twilio Phone Number', blank=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='twilio_sid',
            field=models.CharField(max_length=100, null=True, verbose_name='Twilio Sid', blank=True),
        ),
    ]
