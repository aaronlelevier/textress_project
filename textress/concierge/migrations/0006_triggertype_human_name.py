# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0005_auto_20151011_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='triggertype',
            name='human_name',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
