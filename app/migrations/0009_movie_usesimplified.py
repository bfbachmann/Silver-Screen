# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-17 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_movie_simplifiedtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='useSimplified',
            field=models.BooleanField(default=False),
        ),
    ]