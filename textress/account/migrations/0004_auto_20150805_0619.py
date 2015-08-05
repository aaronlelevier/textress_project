# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150731_0611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accttrans',
            options={'ordering': ('-insert_date',), 'verbose_name': 'Account Transaction'},
        ),
        migrations.AddField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(default=0, help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='balance',
            field=models.PositiveIntegerField(default=0, help_text=b'Monthly Cost + (SMS Used * Cost Per SMS)', verbose_name='Current Funds Balance', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='month',
            field=models.PositiveIntegerField(verbose_name='Month', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='monthly_costs',
            field=models.PositiveIntegerField(default=0, verbose_name='Total Monthly Cost', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='total_sms',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='year',
            field=models.PositiveIntegerField(verbose_name='Year', blank=True),
        ),
        migrations.AlterField(
            model_name='accttrans',
            name='amount',
            field=models.IntegerField(help_text=b"Negative for Usage, Positive for 'Funds Added' records.", null=True, verbose_name='Amount', blank=True),
        ),
        migrations.AlterField(
            model_name='accttrans',
            name='sms_used',
            field=models.PositiveIntegerField(help_text=b'NULL unless trans_type=sms_used', null=True, blank=True),
        ),
    ]
