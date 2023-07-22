# Generated by Django 4.1.4 on 2023-04-28 20:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0014_alter_teacherjournal_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='address',
            field=models.CharField(default='МО', max_length=200, verbose_name='Место проживания'),
        ),
        migrations.AddField(
            model_name='client',
            name='birthday',
            field=models.DateField(default=datetime.date(2023, 4, 28), verbose_name='Дата рождения'),
        ),
    ]