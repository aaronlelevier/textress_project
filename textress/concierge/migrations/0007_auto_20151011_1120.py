# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0006_triggertype_human_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triggertype',
            name='name',
            field=models.CharField(help_text=b'name to be referenced in the application code.', unique=True, max_length=100),
        ),
    ]
