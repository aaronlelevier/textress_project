# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='acctcost',
            name='per_sms',
        ),
        migrations.AlterField(
            model_name='acctcost',
            name='balance_min',
            field=models.PositiveIntegerField(default=100, verbose_name='Balance Minimum', choices=[(100, '$1.00'), (1000, '$10.00'), (2000, '$20.00'), (3000, '$30.00'), (4000, '$40.00'), (5000, '$50.00'), (6000, '$60.00'), (7000, '$70.00'), (8000, '$80.00'), (9000, '$90.00'), (10000, '$100.00')]),
            preserve_default=True,
        ),
    ]
