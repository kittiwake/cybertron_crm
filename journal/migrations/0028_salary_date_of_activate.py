# Generated by Django 4.2.1 on 2023-06-22 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0027_timetable_hours_payed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salary',
            name='date_of_activate',
            field=models.DateTimeField(default='2023-01-01', verbose_name='Действительна с '),
            preserve_default=False,
        ),
    ]
