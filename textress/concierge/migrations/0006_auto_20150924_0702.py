# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0005_auto_20150923_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reply',
            name='letter',
            field=models.CharField(help_text=b'Letter(s) will be upper cased automatically. Single letters encouraged for shorter SMS, but not enforced.', max_length=1, verbose_name='Letter(s)'),
        ),
    ]
