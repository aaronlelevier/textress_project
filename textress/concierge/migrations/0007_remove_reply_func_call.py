# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0006_auto_20150924_0702'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='func_call',
        ),
    ]
