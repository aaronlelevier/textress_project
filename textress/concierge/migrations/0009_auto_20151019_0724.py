# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0008_auto_20151011_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='phone_number',
            field=models.CharField(help_text=b'10 Digit Phone Number. Example: 7025101234', max_length=12, verbose_name='Phone Number'),
        ),
    ]
