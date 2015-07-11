# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150711_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcctCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('init_amt', models.PositiveIntegerField(default=100, verbose_name='Amount to Add', choices=[(100, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('balance_min', models.PositiveIntegerField(default=100, verbose_name='Balance Minimum', choices=[(100, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('recharge_amt', models.PositiveIntegerField(default=100, verbose_name='Recharge Amount', choices=[(100, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')])),
                ('hotel', models.OneToOneField(related_name='acct_cost', to='main.Hotel')),
            ],
            options={
                'verbose_name': 'Account Cost',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='AcctStmt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(verbose_name='Year', blank=True)),
                ('month', models.IntegerField(verbose_name='Month', blank=True)),
                ('monthly_costs', models.FloatField(default=0, verbose_name='Total Monthly Cost', blank=True)),
                ('total_sms', models.IntegerField(default=0, blank=True)),
                ('balance', models.FloatField(default=0, help_text=b'Monthly Cost + (SMS Used * Cost Per SMS)', verbose_name='Current Funds Balance', blank=True)),
                ('hotel', models.ForeignKey(related_name='acct_stmt', to='main.Hotel')),
            ],
            options={
                'verbose_name': 'Account Statement',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='AcctTrans',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(help_text=b"Negative for Usage, Positive for 'Funds Added' records.", null=True, verbose_name='Amount', blank=True)),
                ('sms_used', models.IntegerField(help_text=b'NULL unless trans_type=sms_used', null=True, blank=True)),
                ('insert_date', models.DateField(null=True, verbose_name='Insert Date', blank=True)),
                ('hotel', models.ForeignKey(related_name='acct_trans', to='main.Hotel')),
            ],
            options={
                'verbose_name': 'Account Transaction',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('tier', models.PositiveIntegerField(verbose_name='Tier')),
                ('tier_name', models.CharField(help_text=b"If blank, will be the Tier's Price per SMS", max_length=55, verbose_name='Tier Name', blank=True)),
                ('desc', models.CharField(help_text=b'Used for Pricing Biz Page Description.', max_length=255, verbose_name='Description', blank=True)),
                ('price', models.DecimalField(help_text=b"Price in $'s. Ex: 0.0525", verbose_name='Price per SMS', max_digits=5, decimal_places=4)),
                ('start', models.PositiveIntegerField(help_text=b'Min SMS per Tier', verbose_name='SMS Start')),
                ('end', models.PositiveIntegerField(help_text=b'Max SMS per Tier', verbose_name='SMS End')),
            ],
            options={
                'ordering': ('tier',),
                'verbose_name_plural': 'Pricing',
            },
            bases=(account.models.Dates, models.Model),
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
                'ordering': ['id'],
                'verbose_name': 'Transaction Type',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.AddField(
            model_name='accttrans',
            name='trans_type',
            field=models.ForeignKey(to='account.TransType'),
        ),
    ]
