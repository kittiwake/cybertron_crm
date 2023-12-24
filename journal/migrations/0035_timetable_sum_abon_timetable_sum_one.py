# Generated by Django 4.2.1 on 2023-12-13 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0034_paying_accepted_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='sum_abon',
            field=models.IntegerField(default=4000, verbose_name='Абонемент'),
        ),
        migrations.AddField(
            model_name='timetable',
            name='sum_one',
            field=models.IntegerField(default=1100, verbose_name='Сумма за час'),
        ),
    ]