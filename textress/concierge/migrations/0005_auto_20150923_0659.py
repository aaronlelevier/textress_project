# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0004_auto_20150829_0629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reply',
            name='func_call',
            field=models.CharField(help_text=b'Configure the string name of a function call here for User requested data changes', max_length=100, verbose_name='Function Call', blank=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='hotel',
            field=models.ForeignKey(blank=True, to='main.Hotel', null=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='letter',
            field=models.CharField(help_text=b'Letter(s) will be upper cased automatically. Single letters encouraged for shorter SMS, but not enforced.', max_length=25, verbose_name='Letter(s)'),
        ),
    ]
