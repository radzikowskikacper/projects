# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-14 15:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lecturers', '0001_initial'),
        ('common', '0005_auto_20170207_1347'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('lecturer', 'title', 'course')]),
        ),
    ]