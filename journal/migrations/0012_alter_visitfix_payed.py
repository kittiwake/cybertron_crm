# Generated by Django 4.0.5 on 2022-07-31 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0011_remove_visitfix_active_timetable_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitfix',
            name='payed',
            field=models.ForeignKey(blank=True, on_delete=models.SET(False), to='journal.paying', verbose_name='Дата оплаты'),
        ),
    ]
