# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 17:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Team', verbose_name='team')),
            ],
            options={
                'verbose_name_plural': 'students',
                'verbose_name': 'student',
                'ordering': ['user__username'],
            },
        ),
    ]
