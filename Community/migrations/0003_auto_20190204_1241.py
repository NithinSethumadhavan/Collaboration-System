# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-04 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Community', '0002_auto_20181224_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestcommunitycreation',
            name='status',
            field=models.CharField(default='Request', max_length=100, null=True),
        ),
    ]