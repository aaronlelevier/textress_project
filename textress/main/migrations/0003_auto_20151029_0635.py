# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20151029_0619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
    ]
