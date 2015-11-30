# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcctCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('init_amt', models.PositiveIntegerField(default=500, verbose_name='Amount to Add', choices=[(500, b'$5.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('balance_min', models.PositiveIntegerField(default=100, verbose_name='Balance Minimum', choices=[(100, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('recharge_amt', models.PositiveIntegerField(default=500, help_text=b'A higher Recharge Amount is recommended to decrease payment transactions.', verbose_name='Recharge Amount', choices=[(500, b'$5.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('auto_recharge', models.BooleanField(default=True, verbose_name=b'Auto Recharge On')),
            ],
            options={
                'verbose_name': 'Account Cost',
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='AcctStmt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('year', models.PositiveIntegerField()),
                ('month', models.PositiveIntegerField()),
                ('funds_added', models.PositiveIntegerField(default=0, help_text=b"from 'init_amt' or 'recharge_amt' AcctTrans.", blank=True)),
                ('phone_numbers', models.PositiveIntegerField(default=0, blank=True)),
                ('monthly_costs', models.IntegerField(default=0, help_text=b'Only active Phone Numbers have a monthly cost at this time, but other costs may be added. Additional feature costs, surcharge for REST API access, etc...', blank=True)),
                ('total_sms', models.PositiveIntegerField(default=0, blank=True)),
                ('total_sms_costs', models.IntegerField(default=0, help_text=b'This will be negative (debits are negative).', blank=True)),
                ('balance', models.IntegerField(default=0, verbose_name='Current Funds Balance', blank=True)),
            ],
            options={
                'ordering': ('-year', '-month'),
                'verbose_name': 'Account Statement',
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='AcctTrans',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('amount', models.IntegerField(help_text=b"Negative for Usage, Positive for 'Funds Added' records.", null=True, verbose_name='Amount', blank=True)),
                ('desc', models.CharField(help_text=b'Use to store additional filter logic', max_length=100, null=True, blank=True)),
                ('sms_used', models.PositiveIntegerField(default=0, help_text=b'NULL unless trans_type=sms_used', blank=True)),
                ('insert_date', models.DateField(null=True, verbose_name='Insert Date', blank=True)),
                ('balance', models.PositiveIntegerField(help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True)),
            ],
            options={
                'ordering': ('-insert_date',),
                'verbose_name': 'Account Transaction',
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cost', models.FloatField(default=5.0, help_text=b'Price in Stripe units, so -> 5.00 == $0.05', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Pricing',
            },
            bases=(utils.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='TransType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Name')),
                ('desc', models.CharField(max_length=255, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Transaction Type',
            },
            bases=(utils.models.Dates, models.Model),
        ),
    ]
