# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import account.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcctCost',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('per_sms', models.FloatField(blank=True, verbose_name='Per SMS Cost', default=5.5)),
                ('init_amt', models.PositiveIntegerField(choices=[(1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')], verbose_name='Amount to Add', default=1000)),
                ('balance_min', models.IntegerField(choices=[(0, '$0.00'), (1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')], verbose_name='Balance Minimum', default=0)),
                ('recharge_amt', models.PositiveIntegerField(choices=[(1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')], verbose_name='Recharge Amount', default=1000)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(blank=True, verbose_name='Year')),
                ('month', models.IntegerField(blank=True, verbose_name='Month')),
                ('monthly_costs', models.FloatField(blank=True, verbose_name='Total Monthly Cost', default=500.0)),
                ('total_sms', models.IntegerField(blank=True, default=0)),
                ('balance', models.FloatField(help_text='Monthly Cost + (SMS Used * Cost Per SMS)', blank=True, verbose_name='Current Funds Balance', default=0)),
                ('hotel', models.ForeignKey(to='main.Hotel', related_name='acct_stmt')),
            ],
            options={
                'verbose_name': 'Account Statement',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='AcctTrans',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField(help_text="Negative for Usage, Positive for 'Funds Added' records.", blank=True, verbose_name='Amount', null=True)),
                ('sms_used', models.IntegerField(help_text='NULL unless trans_type=sms_used', blank=True, null=True, default=0)),
                ('insert_date', models.DateField(blank=True, verbose_name='Insert Date', null=True)),
                ('debit', models.BooleanField(verbose_name='Acct Debit', default=False)),
                ('credit', models.BooleanField(verbose_name='Acct Credit', default=False)),
                ('hotel', models.ForeignKey(to='main.Hotel', related_name='acct_trans')),
            ],
            options={
                'verbose_name': 'Account Transaction',
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('tier', models.PositiveIntegerField(verbose_name='Tier')),
                ('tier_name', models.CharField(help_text="If blank, will be the Tier's Price per SMS", blank=True, verbose_name='Tier Name', max_length=55)),
                ('desc', models.CharField(help_text='Used for Pricing Biz Page Description.', blank=True, verbose_name='Description', max_length=255)),
                ('price', models.DecimalField(help_text="Price in $'s. Ex: 0.0525", max_digits=5, verbose_name='Price per SMS', decimal_places=4)),
                ('start', models.PositiveIntegerField(help_text='Min SMS per Tier', verbose_name='SMS Start')),
                ('end', models.PositiveIntegerField(help_text='Max SMS per Tier', verbose_name='SMS End')),
            ],
            options={
                'verbose_name_plural': 'Pricing',
                'ordering': ('tier',),
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.CreateModel(
            name='TransType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(verbose_name='Name', max_length=50, unique=True)),
                ('desc', models.CharField(verbose_name='Description', max_length=255)),
            ],
            options={
                'verbose_name': 'Transaction Type',
                'ordering': ['id'],
            },
            bases=(account.models.Dates, models.Model),
        ),
        migrations.AddField(
            model_name='accttrans',
            name='trans_type',
            field=models.ForeignKey(to='account.TransType'),
            preserve_default=True,
        ),
    ]
