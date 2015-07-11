# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import payment.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('short_pk', models.CharField(max_length=10, verbose_name='Short PK', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=100, serialize=False, verbose_name='Stripe Card ID', primary_key=True)),
                ('brand', models.CharField(max_length=25, verbose_name='Brand')),
                ('last4', models.PositiveIntegerField(verbose_name='Last 4')),
                ('exp_month', models.PositiveIntegerField(verbose_name='Exp Month')),
                ('exp_year', models.PositiveIntegerField(verbose_name='Exp Year')),
                ('default', models.BooleanField(default=True, verbose_name='Default')),
                ('expires', models.CharField(max_length=10, verbose_name='Expires', blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
            bases=(payment.models.StripeClient, models.Model),
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('short_pk', models.CharField(max_length=10, verbose_name='Short PK', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=100, serialize=False, verbose_name='Stripe Charge ID', primary_key=True)),
                ('amount', models.PositiveIntegerField(help_text=b'Stripe Cost Amount of the Charge in cents. Ex: 2000 ~ $20', verbose_name='Stripe Amount')),
                ('card', models.ForeignKey(to='payment.Card')),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
            bases=(payment.models.StripeClient, models.Model),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('short_pk', models.CharField(max_length=10, verbose_name='Short PK', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=100, serialize=False, verbose_name='Stripe Customer ID', primary_key=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
            bases=(payment.models.StripeClient, models.Model),
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('short_pk', models.CharField(max_length=10, verbose_name='Short PK', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=100, serialize=False, verbose_name='Stripe Refund ID', primary_key=True)),
                ('amount', models.PositiveIntegerField(help_text=b'Stripe Cost Amount of the Charge. Ex: 2000 ~ $20', verbose_name='Stripe Amount')),
                ('charge', models.ForeignKey(related_name='refunds', to='payment.Charge')),
            ],
            options={
                'ordering': ['-created'],
                'abstract': False,
            },
            bases=(payment.models.StripeClient, models.Model),
        ),
        migrations.AddField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(to='payment.Customer'),
        ),
        migrations.AddField(
            model_name='card',
            name='customer',
            field=models.ForeignKey(related_name='cards', to='payment.Customer'),
        ),
    ]
