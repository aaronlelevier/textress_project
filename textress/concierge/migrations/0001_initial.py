# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(help_text=b'Full name of the Guest as you would like to call them.', max_length=110, verbose_name='Name')),
                ('room_number', models.CharField(max_length=10, verbose_name='Room Number')),
                ('phone_number', models.CharField(help_text=b'10 Digit Phone Number. Example: 7025101234', unique=True, max_length=12, verbose_name='Phone Number')),
                ('check_in', models.DateField(help_text=b'If left blank, Check-in Date will be today.', verbose_name='Check-in Date', blank=True)),
                ('check_out', models.DateField(verbose_name='Check-out Date', blank=True)),
                ('confirmed', models.BooleanField(default=False, help_text=b"Reply 'Y' to Confirm PH # for example.", verbose_name='Confirmed')),
                ('stop', models.BooleanField(default=False, help_text=b"Reply 'S' to Stop receiving all messages.", verbose_name='Stop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('sid', models.CharField(null=True, max_length=55, blank=True, help_text=b"If the message failed to send, there won't be a Twilio Sid.", unique=True, verbose_name='Twilio Sid')),
                ('received', models.NullBooleanField(default=False, verbose_name='Received')),
                ('status', models.CharField(max_length=25, null=True, verbose_name='Status', blank=True)),
                ('to_ph', models.CharField(max_length=12, verbose_name='To', blank=True)),
                ('from_ph', models.CharField(default=b'+17024302691', max_length=12, verbose_name='From', blank=True)),
                ('body', models.TextField(max_length=320, verbose_name='Message')),
                ('reason', models.CharField(help_text=b'Reason for failure of SMS send, else Null.', max_length=100, null=True, verbose_name='Error Code Reason', blank=True)),
                ('cost', models.FloatField(null=True, blank=True)),
                ('insert_date', models.DateField(null=True, verbose_name='Insert Date', blank=True)),
                ('read', models.BooleanField(default=False, help_text=b'All messages are unread until rendered in a User View.', verbose_name='Read')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('letter', models.CharField(help_text=b'Letter(s) will be upper cased automatically. Single letters encouraged for shorter SMS, but not enforced.', max_length=1, verbose_name='Letter(s)')),
                ('message', models.CharField(max_length=320, verbose_name='Auto Reply Message', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Replies',
            },
        ),
    ]
