# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-30 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='Actors',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='BoxOffice',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='Director',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='Genres',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='Poster',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='Year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='YomatoURL',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdbRating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='plot',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='tomatoConsensus',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='tomatoRating',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='tomatorUserRating',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]