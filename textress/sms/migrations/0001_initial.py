# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150711_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('sid', models.CharField(max_length=50, serialize=False, verbose_name='Twilio Phone # Sid', primary_key=True)),
                ('phone_number', models.CharField(max_length=12, verbose_name='Twilio Phone #')),
                ('friendly_name', models.CharField(max_length=14, verbose_name='Twilio Friendly Name', blank=True)),
                ('is_primary', models.BooleanField(default=True, help_text=b'only 1 phone number can be the primary', verbose_name='Is Primary')),
                ('hotel', models.ForeignKey(related_name='phonenumbers', to='main.Hotel')),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
            bases=(main.models.TwilioClient, models.Model),
        ),
    ]
