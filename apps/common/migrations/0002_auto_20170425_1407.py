# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-25 12:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        ('lecturers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='lecturer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lecturers.Lecturer', verbose_name='lecturer'),
        ),
        migrations.AddField(
            model_name='project',
            name='team_assigned',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Team', verbose_name='team assigned'),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('lecturer', 'title', 'course')]),
        ),
    ]
