# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 00:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_movie_recentvisits'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='Genres',
            new_name='Genre',
        ),
        migrations.RenameField(
            model_name='movie',
            old_name='plot',
            new_name='Plot',
        ),
        migrations.RenameField(
            model_name='movie',
            old_name='TomatoURL',
            new_name='tomatoURL',
        ),
    ]
