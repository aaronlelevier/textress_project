# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20151002_0609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctcost',
            name='init_amt',
            field=models.PositiveIntegerField(default=500, verbose_name='Amount to Add', choices=[(500, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')]),
        ),
        migrations.AlterField(
            model_name='acctcost',
            name='recharge_amt',
            field=models.PositiveIntegerField(default=500, verbose_name='Recharge Amount', choices=[(500, b'$1.00'), (1000, b'$10.00'), (2000, b'$20.00'), (3000, b'$30.00'), (4000, b'$40.00'), (5000, b'$50.00'), (6000, b'$60.00'), (7000, b'$70.00'), (8000, b'$80.00'), (9000, b'$90.00'), (10000, b'$100.00')]),
        ),
    ]
