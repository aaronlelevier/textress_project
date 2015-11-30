# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import main.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Hotel Name')),
                ('address_phone', models.CharField(help_text=b'Allowed phone number format: (702) 510-5555', unique=True, max_length=12, verbose_name='Contact Phone Number')),
                ('address_line1', models.CharField(max_length=100, verbose_name='Address Line 1')),
                ('address_city', models.CharField(max_length=100, verbose_name='City')),
                ('address_state', models.CharField(default=b'Alabama', max_length=25, verbose_name='State', choices=[(b'Alabama', b'Alabama'), (b'Alaska', b'Alaska'), (b'Arizona', b'Arizona'), (b'Arkansas', b'Arkansas'), (b'California', b'California'), (b'Colorado', b'Colorado'), (b'Connecticut', b'Connecticut'), (b'Delaware', b'Delaware'), (b'District of Columbia', b'District of Columbia'), (b'Florida', b'Florida'), (b'Georgia', b'Georgia'), (b'Hawaii', b'Hawaii'), (b'Idaho', b'Idaho'), (b'Illinois', b'Illinois'), (b'Indiana', b'Indiana'), (b'Iowa', b'Iowa'), (b'Kansas', b'Kansas'), (b'Kentucky', b'Kentucky'), (b'Louisiana', b'Louisiana'), (b'Maine', b'Maine'), (b'Maryland', b'Maryland'), (b'Massachusetts', b'Massachusetts'), (b'Michigan', b'Michigan'), (b'Minnesota', b'Minnesota'), (b'Mississippi', b'Mississippi'), (b'Missouri', b'Missouri'), (b'Montana', b'Montana'), (b'Nebraska', b'Nebraska'), (b'Nevada', b'Nevada'), (b'New Hampshire', b'New Hampshire'), (b'New Jersey', b'New Jersey'), (b'New Mexico', b'New Mexico'), (b'New York', b'New York'), (b'North Carolina', b'North Carolina'), (b'North Dakota', b'North Dakota'), (b'Ohio', b'Ohio'), (b'Oklahoma', b'Oklahoma'), (b'Oregon', b'Oregon'), (b'Pennsylvania', b'Pennsylvania'), (b'Rhode Island', b'Rhode Island'), (b'South Carolina', b'South Carolina'), (b'South Dakota', b'South Dakota'), (b'Tennessee', b'Tennessee'), (b'Texas', b'Texas'), (b'Utah', b'Utah'), (b'Vermont', b'Vermont'), (b'Virginia', b'Virginia'), (b'Washington', b'Washington'), (b'West Virginia', b'West Virginia'), (b'Wisconsin', b'Wisconsin'), (b'Wyoming', b'Wyoming')])),
                ('address_zip', models.PositiveIntegerField(help_text=b'5-digit zipcode. i.e.: 89109', verbose_name='Zipcode')),
                ('address_line2', models.CharField(max_length=100, verbose_name='Address Line 2', blank=True)),
                ('hotel_type', models.CharField(default=b'', max_length=100, verbose_name='Hotel Type', blank=True, choices=[(b'Bed and breakfast', b'Bed and breakfast'), (b'Boutique hotel', b'Boutique hotel'), (b'Business hotel', b'Business hotel'), (b'Casino hotel', b'Casino hotel'), (b'Conference hotel', b'Conference hotel'), (b'Extended stay hotel', b'Extended stay hotel'), (b'Hostel', b'Hostel'), (b'Hotel', b'Hotel'), (b'Inn', b'Inn'), (b'Motel', b'Motel'), (b'Resort hotel', b'Resort hotel')])),
                ('rooms', models.IntegerField(null=True, verbose_name='Rooms', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=125, verbose_name='Slug', blank=True)),
                ('active', models.BooleanField(default=True, help_text=b'Deactivate Hotel here when they run out of funds to send SMS.')),
                ('group_name', models.CharField(max_length=100, blank=True)),
                ('admin_id', models.IntegerField(help_text=b'1 Hotel Admin User per Hotel', unique=True, null=True, verbose_name='Hotel Admin ID', blank=True)),
                ('twilio_sid', models.CharField(max_length=100, null=True, verbose_name='Twilio Sid', blank=True)),
                ('twilio_auth_token', models.CharField(max_length=100, null=True, verbose_name='Twilio Auth Token', blank=True)),
                ('twilio_phone_number', models.CharField(max_length=25, null=True, verbose_name='Twilio Phone Number', blank=True)),
                ('twilio_ph_sid', models.CharField(max_length=100, null=True, verbose_name='Twilio Phone Number Sid', blank=True)),
                ('customer', models.ForeignKey(blank=True, to='payment.Customer', help_text=b'Stripe Customer Id', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(main.models.TwilioClient, models.Model),
        ),
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, null=True, blank=True)),
                ('icon', models.ImageField(null=True, upload_to=main.models.profile_image, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subaccount',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('sid', models.CharField(max_length=100, serialize=False, verbose_name='Twilio Subaccount Sid', primary_key=True)),
                ('auth_token', models.CharField(max_length=100, verbose_name='Auth Token')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('hotel', models.OneToOneField(related_name='subaccount', to='main.Hotel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('msg_sign', models.CharField(max_length=25, verbose_name='Message Signature', blank=True)),
                ('hotel', models.ForeignKey(blank=True, to='main.Hotel', null=True)),
                ('icon', models.ForeignKey(blank=True, to='main.Icon', null=True)),
            ],
            options={
                'permissions': (('hotel_admin', 'hotel_admin'), ('hotel_manager', 'hotel_manager')),
            },
        ),
    ]
