# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-21 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0002_auto_20161221_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcesentence',
            name='word_map',
            field=models.TextField(default=''),
        ),
    ]
