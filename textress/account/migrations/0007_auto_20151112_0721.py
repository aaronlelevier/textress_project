# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_auto_20151107_1306'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transtype',
            options={'verbose_name': 'Transaction Type'},
        ),
    ]
