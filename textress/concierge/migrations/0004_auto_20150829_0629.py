# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150829_0629'),
        ('concierge', '0003_auto_20150823_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='guest',
            name='icon',
            field=models.ForeignKey(blank=True, to='main.Icon', null=True),
        ),
    ]
