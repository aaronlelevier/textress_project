# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0002_auto_20151129_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='guest',
            field=models.ForeignKey(to='concierge.Guest', null=True),
        ),
    ]
