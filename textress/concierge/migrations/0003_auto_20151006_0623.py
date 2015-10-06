# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0002_auto_20151002_0609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='reason',
            field=models.CharField(help_text=b'Reason for failure of SMS send, else Null.', max_length=500, null=True, verbose_name='Error Code Reason', blank=True),
        ),
    ]
