# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-04 04:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_merge_20161203_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='imdbID',
            field=models.CharField(max_length=1024, unique=True),
        ),
    ]