# Generated by Django 4.2.1 on 2023-06-20 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0026_remove_visitfix_payed_paying_used_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='hours_payed',
            field=models.DecimalField(decimal_places=1, default=2.0, max_digits=2, verbose_name='Часов на оплату'),
        ),
        migrations.AlterField(
            model_name='teacherjournal',
            name='date_of_paid',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выплаты'),
        ),
        migrations.AlterField(
            model_name='teacherjournal',
            name='id_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.teacher', verbose_name='Преподаватель'),
        ),
    ]