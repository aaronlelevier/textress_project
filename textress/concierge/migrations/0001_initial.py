# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.models


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
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('name', models.CharField(help_text=b'Full name of the Guest as you would like to call them.', max_length=110, verbose_name='Name')),
                ('room_number', models.CharField(max_length=10, verbose_name='Room Number')),
                ('phone_number', models.CharField(help_text=b'Allowed phone number format: (702) 510-5555', max_length=12, verbose_name='Phone Number')),
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
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('sid', models.CharField(null=True, max_length=55, blank=True, help_text=b"If the message failed to send, there won't be a Twilio Sid.", unique=True, verbose_name='Twilio Sid')),
                ('received', models.NullBooleanField(default=False, verbose_name='Received')),
                ('status', models.CharField(max_length=25, null=True, verbose_name='Status', blank=True)),
                ('to_ph', models.CharField(max_length=12, verbose_name='To', blank=True)),
                ('from_ph', models.CharField(default=b'+17024302691', max_length=12, verbose_name='From', blank=True)),
                ('body', models.TextField(max_length=320, verbose_name='Message')),
                ('reason', models.CharField(help_text=b'Reason for failure of SMS send, else Null.', max_length=500, null=True, verbose_name='Error Code Reason', blank=True)),
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
                ('letter', models.CharField(default=b'A', help_text=b'Letter(s) will be upper cased automatically. Single letters encouraged for shorter SMS, but not enforced.', max_length=1, verbose_name='Letter(s)', choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E'), (b'F', b'F'), (b'G', b'G'), (b'H', b'H'), (b'I', b'I'), (b'J', b'J'), (b'K', b'K'), (b'L', b'L'), (b'M', b'M'), (b'N', b'N'), (b'O', b'O'), (b'P', b'P'), (b'Q', b'Q'), (b'R', b'R'), (b'S', b'S'), (b'T', b'T'), (b'U', b'U'), (b'V', b'V'), (b'W', b'W'), (b'X', b'X'), (b'Y', b'Y'), (b'Z', b'Z')])),
                ('desc', models.CharField(max_length=254, verbose_name='Description', blank=True)),
                ('message', models.CharField(max_length=320, verbose_name='Auto Reply Message', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Replies',
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='TriggerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'name to be referenced in the application code.', unique=True, max_length=100)),
                ('human_name', models.CharField(max_length=100, blank=True)),
                ('desc', models.CharField(help_text=b"Use to store information about what each Trigger type will actually do. i.e. 'check_in' will be used to send welcome messages.", max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.models.Dates, models.Model),
        ),
    ]
