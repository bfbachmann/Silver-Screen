# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-30 23:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_tweet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tweetID',
            field=models.BigIntegerField(),
        ),
    ]
