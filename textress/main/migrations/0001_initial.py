# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('payment', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(verbose_name='Hide', default=False)),
                ('name', models.CharField(verbose_name='Hotel Name', max_length=100, unique=True)),
                ('address_phone', models.CharField(help_text='10-digit phone number. i.e.: 7025101234', verbose_name='Contact Phone Number', max_length=12, unique=True)),
                ('address_line1', models.CharField(verbose_name='Address Line 1', max_length=100)),
                ('address_city', models.CharField(verbose_name='City', max_length=100)),
                ('address_state', models.CharField(default='Alabama', verbose_name='State', max_length=25, choices=[('Alabama', 'Alabama'), ('Alaska', 'Alaska'), ('Arizona', 'Arizona'), ('Arkansas', 'Arkansas'), ('California', 'California'), ('Colorado', 'Colorado'), ('Connecticut', 'Connecticut'), ('Delaware', 'Delaware'), ('District of Columbia', 'District of Columbia'), ('Florida', 'Florida'), ('Georgia', 'Georgia'), ('Hawaii', 'Hawaii'), ('Idaho', 'Idaho'), ('Illinois', 'Illinois'), ('Indiana', 'Indiana'), ('Iowa', 'Iowa'), ('Kansas', 'Kansas'), ('Kentucky', 'Kentucky'), ('Louisiana', 'Louisiana'), ('Maine', 'Maine'), ('Maryland', 'Maryland'), ('Massachusetts', 'Massachusetts'), ('Michigan', 'Michigan'), ('Minnesota', 'Minnesota'), ('Mississippi', 'Mississippi'), ('Missouri', 'Missouri'), ('Montana', 'Montana'), ('Nebraska', 'Nebraska'), ('Nevada', 'Nevada'), ('New Hampshire', 'New Hampshire'), ('New Jersey', 'New Jersey'), ('New Mexico', 'New Mexico'), ('New York', 'New York'), ('North Carolina', 'North Carolina'), ('North Dakota', 'North Dakota'), ('Ohio', 'Ohio'), ('Oklahoma', 'Oklahoma'), ('Oregon', 'Oregon'), ('Pennsylvania', 'Pennsylvania'), ('Rhode Island', 'Rhode Island'), ('South Carolina', 'South Carolina'), ('South Dakota', 'South Dakota'), ('Tennessee', 'Tennessee'), ('Texas', 'Texas'), ('Utah', 'Utah'), ('Vermont', 'Vermont'), ('Virginia', 'Virginia'), ('Washington', 'Washington'), ('West Virginia', 'West Virginia'), ('Wisconsin', 'Wisconsin'), ('Wyoming', 'Wyoming')])),
                ('address_zip', models.PositiveIntegerField(help_text='5-digit zipcode. i.e.: 89109', verbose_name='Zipcode', max_length=5)),
                ('address_line2', models.CharField(blank=True, verbose_name='Address Line 2', max_length=100)),
                ('hotel_type', models.CharField(blank=True, default='', verbose_name='Hotel Type', max_length=100, choices=[('Bed and breakfast', 'Bed and breakfast'), ('Boutique hotel', 'Boutique hotel'), ('Business hotel', 'Business hotel'), ('Casino hotel', 'Casino hotel'), ('Conference hotel', 'Conference hotel'), ('Extended stay hotel', 'Extended stay hotel'), ('Hostel', 'Hostel'), ('Hotel', 'Hotel'), ('Inn', 'Inn'), ('Motel', 'Motel'), ('Resort hotel', 'Resort hotel')])),
                ('rooms', models.IntegerField(blank=True, null=True, verbose_name='Rooms', max_length=5)),
                ('slug', models.SlugField(blank=True, verbose_name='Slug', max_length=125, unique=True)),
                ('active', models.BooleanField(help_text='Deactivate Hotel here when they run out of funds to send SMS.', default=True)),
                ('admin_id', models.IntegerField(blank=True, help_text='1 Hotel Admin User per Hotel', verbose_name='Hotel Admin ID', unique=True, null=True)),
                ('twilio_sid', models.CharField(blank=True, verbose_name='Twilio Sid', max_length=100)),
                ('twilio_auth_token', models.CharField(blank=True, verbose_name='Twilio Auth Token', max_length=100)),
                ('twilio_phone_number', models.CharField(blank=True, verbose_name='Twilio Phone Number', max_length=12)),
                ('twilio_ph_sid', models.CharField(blank=True, verbose_name='Twilio Phone Number Sid', max_length=100)),
                ('customer', models.ForeignKey(blank=True, help_text='Stripe Customer Id', to='payment.Customer', null=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['-created'],
            },
            bases=(main.models.TwilioClient, models.Model),
        ),
        migrations.CreateModel(
            name='Subaccount',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(verbose_name='Hide', default=False)),
                ('sid', models.CharField(primary_key=True, serialize=False, verbose_name='Twilio Subaccount Sid', max_length=100)),
                ('auth_token', models.CharField(verbose_name='Auth Token', max_length=100)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
                ('hotel', models.OneToOneField(to='main.Hotel', related_name='subaccount')),
            ],
            options={
                'abstract': False,
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(verbose_name='Hide', default=False)),
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, related_name='profile')),
                ('msg_sign', models.CharField(blank=True, verbose_name='Message Signature', max_length=25)),
                ('hotel', models.ForeignKey(blank=True, null=True, to='main.Hotel')),
            ],
            options={
                'permissions': (('hotel_admin', 'hotel_admin'), ('hotel_manager', 'hotel_manager')),
            },
            bases=(models.Model,),
        ),
    ]
