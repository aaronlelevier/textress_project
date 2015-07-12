# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=main.models.profile_image, blank=True),
        ),
    ]
