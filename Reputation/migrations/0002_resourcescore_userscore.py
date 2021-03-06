# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-21 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reputation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_vote', models.BooleanField(default=True)),
                ('upvote_value', models.IntegerField()),
                ('downvote_value', models.IntegerField()),
                ('can_report', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.IntegerField()),
                ('publisher', models.IntegerField()),
            ],
        ),
    ]
