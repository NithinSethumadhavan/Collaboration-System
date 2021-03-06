# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-17 08:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Media', '0001_initial'),
        ('Group', '0013_groupinvitations'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmedia', to='Group.Group')),
                ('media', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmedia', to='Media.Media')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmedia', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
