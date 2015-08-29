# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150712_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('icon', models.ImageField(null=True, upload_to=main.models.profile_image, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='icon',
            field=models.ForeignKey(blank=True, to='main.Icon', null=True),
        ),
    ]
