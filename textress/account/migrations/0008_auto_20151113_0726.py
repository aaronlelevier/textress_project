# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20151112_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accttrans',
            name='sms_used',
            field=models.PositiveIntegerField(default=0, help_text=b'NULL unless trans_type=sms_used', blank=True),
        ),
    ]
