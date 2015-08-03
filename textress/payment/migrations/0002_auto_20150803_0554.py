# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import payment.models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to=payment.models.card_image_file)),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='image',
            field=models.ForeignKey(blank=True, to='payment.CardImage', help_text=b'Auto-add the CardImage at save() based on Card.brand', null=True),
        ),
    ]
