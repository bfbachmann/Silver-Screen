# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-10 02:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20161109_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='recentVisits',
            field=models.IntegerField(default=0),
        ),
    ]
