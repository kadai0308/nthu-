# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-24 09:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_page', '0002_scoredistribution_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='latest_open_time',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]