# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0003_auto_20151006_0623'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='desc',
            field=models.CharField(max_length=254, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='letter',
            field=models.CharField(default=b'A', help_text=b'Letter(s) will be upper cased automatically. Single letters encouraged for shorter SMS, but not enforced.', max_length=1, verbose_name='Letter(s)', choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E'), (b'F', b'F'), (b'G', b'G'), (b'H', b'H'), (b'I', b'I'), (b'J', b'J'), (b'K', b'K'), (b'L', b'L'), (b'M', b'M'), (b'N', b'N'), (b'O', b'O'), (b'P', b'P'), (b'Q', b'Q'), (b'R', b'R'), (b'S', b'S'), (b'T', b'T'), (b'U', b'U'), (b'V', b'V'), (b'W', b'W'), (b'X', b'X'), (b'Y', b'Y'), (b'Z', b'Z')]),
        ),
    ]
