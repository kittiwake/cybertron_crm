# Generated by Django 4.0.5 on 2022-07-25 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0009_alter_client_options_alter_timetable_duration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visitfix',
            options={'ordering': ['date'], 'verbose_name': 'Посещение', 'verbose_name_plural': 'Посещение'},
        ),
        migrations.RemoveField(
            model_name='visitfix',
            name='id_branch',
        ),
        migrations.RemoveField(
            model_name='visitfix',
            name='id_course',
        ),
        migrations.RemoveField(
            model_name='visitfix',
            name='time',
        ),
        migrations.AddField(
            model_name='visitfix',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Включен'),
        ),
        migrations.AddField(
            model_name='visitfix',
            name='id_timetable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='journal.timetable', verbose_name='Расписание'),
        ),
    ]