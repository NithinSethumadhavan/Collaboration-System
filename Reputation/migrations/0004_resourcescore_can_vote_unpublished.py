# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-21 10:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reputation', '0003_auto_20180821_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcescore',
            name='can_vote_unpublished',
            field=models.BooleanField(default=True),
        ),
    ]
