# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-16 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_movie_recentvisits'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='SimplifiedTitle',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]