# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_auto_20151122_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='acctstmt',
            name='funds_added',
            field=models.PositiveIntegerField(default=0, help_text=b"from 'init_amt' or 'recharge_amt' AcctTrans.", blank=True),
        ),
        migrations.AddField(
            model_name='acctstmt',
            name='phone_numbers',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='acctstmt',
            name='total_sms_costs',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='balance',
            field=models.IntegerField(default=0, verbose_name='Current Funds Balance', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='month',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='monthly_costs',
            field=models.PositiveIntegerField(default=0, help_text=b'Only active Phone Numbers have a monthly cost at this time, but other costs may be added. Additional feature costs, surcharge for REST API access, etc...', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='year',
            field=models.PositiveIntegerField(),
        ),
    ]
