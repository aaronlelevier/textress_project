# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150507_0600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctcost',
            name='init_amt',
            field=models.PositiveIntegerField(choices=[(100, '$1.00'), (1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')], default=100, verbose_name='Amount to Add'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='acctcost',
            name='recharge_amt',
            field=models.PositiveIntegerField(choices=[(100, '$1.00'), (1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')], default=100, verbose_name='Recharge Amount'),
            preserve_default=True,
        ),
    ]
