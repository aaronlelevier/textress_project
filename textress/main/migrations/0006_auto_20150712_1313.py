# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_userprofile_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=main.models.profile_image, blank=True),
        ),
    ]
