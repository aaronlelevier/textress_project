# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20150803_0556'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='card',
            options={'ordering': ('-default',)},
        ),
    ]
