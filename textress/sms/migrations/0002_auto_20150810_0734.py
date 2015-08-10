# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phonenumber',
            old_name='is_primary',
            new_name='default',
        ),
    ]
