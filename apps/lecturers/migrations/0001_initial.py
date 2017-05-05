# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 17:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lecturer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('max_students', models.IntegerField(default=20, null=True, verbose_name='students limit')),
            ],
            options={
                'verbose_name': 'lecturer',
                'verbose_name_plural': 'lecturers',
                'ordering': ['user__username'],
            },
        ),
    ]
