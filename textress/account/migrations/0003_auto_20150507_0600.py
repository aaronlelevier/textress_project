# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20150505_0611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accttrans',
            name='credit',
        ),
        migrations.RemoveField(
            model_name='accttrans',
            name='debit',
        ),
        migrations.AlterField(
            model_name='acctstmt',
            name='monthly_costs',
            field=models.FloatField(blank=True, default=0, verbose_name='Total Monthly Cost'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='accttrans',
            name='sms_used',
            field=models.IntegerField(blank=True, help_text='NULL unless trans_type=sms_used', null=True),
            preserve_default=True,
        ),
    ]
