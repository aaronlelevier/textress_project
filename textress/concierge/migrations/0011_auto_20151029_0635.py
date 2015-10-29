# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0010_auto_20151029_0619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='message',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
    ]
