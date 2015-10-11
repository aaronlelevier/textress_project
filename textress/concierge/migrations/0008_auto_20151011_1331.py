# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0007_auto_20151011_1120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='triggertype',
            name='reply',
        ),
        migrations.AddField(
            model_name='trigger',
            name='reply',
            field=models.ForeignKey(default=1, to='concierge.Reply'),
            preserve_default=False,
        ),
    ]
