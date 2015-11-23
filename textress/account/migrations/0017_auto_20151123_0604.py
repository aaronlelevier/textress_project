# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20151122_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acctstmt',
            name='monthly_costs',
            field=models.IntegerField(default=0, help_text=b'Only active Phone Numbers have a monthly cost at this time, but other costs may be added. Additional feature costs, surcharge for REST API access, etc...', blank=True),
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='total_sms_costs',
            field=models.IntegerField(default=0, help_text=b'This will be negative (debits are negative).', blank=True),
        ),
    ]
