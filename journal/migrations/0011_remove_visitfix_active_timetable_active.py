# Generated by Django 4.0.5 on 2022-07-25 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0010_alter_visitfix_options_remove_visitfix_id_branch_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitfix',
            name='active',
        ),
        migrations.AddField(
            model_name='timetable',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Включен'),
        ),
    ]
