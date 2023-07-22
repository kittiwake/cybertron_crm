# Generated by Django 4.0.5 on 2022-07-17 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0007_alter_teacherjournal_number_hours_visitfix'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visitfix',
            options={'ordering': ['time', 'date'], 'verbose_name': 'Посещение', 'verbose_name_plural': 'Посещение'},
        ),
        migrations.AddField(
            model_name='client',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активный'),
        ),
    ]
