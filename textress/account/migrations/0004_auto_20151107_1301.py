# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20151101_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctcost',
            name='init_amt',
            field=models.PositiveIntegerField(default=500, verbose_name='Amount to Add', choices=[(500, b'$5.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')]),
        ),
        migrations.AlterField(
            model_name='acctcost',
            name='recharge_amt',
            field=models.PositiveIntegerField(default=500, help_text=b'A higher Recharge Amount is recommended to decrease payment transactions.', verbose_name='Recharge Amount', choices=[(500, b'$5.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')]),
        ),
        migrations.AlterField(
            model_name='accttrans',
            name='balance',
            field=models.PositiveIntegerField(default=0, help_text=b'Current blance, just like in a Bank Account.', verbose_name='Balance', blank=True),
        ),
    ]
