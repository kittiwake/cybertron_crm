# Generated by Django 4.0.5 on 2022-08-11 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('journal', '0013_alter_visitfix_payed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacherjournal',
            options={'ordering': ['id_teacher', '-date_of_visit', '-ispaid'], 'verbose_name': 'Рабочие часы', 'verbose_name_plural': 'Рабочие часы'},
        ),
        migrations.AddField(
            model_name='teacherjournal',
            name='date_of_paid',
            field=models.DateField(auto_now=True, verbose_name='Дата выплаты'),
        ),
        migrations.AlterField(
            model_name='teacherjournal',
            name='number_hours',
            field=models.DecimalField(decimal_places=1, default=2, max_digits=2, verbose_name='Количество часов'),
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_sum', models.IntegerField(default=0, verbose_name='Сумма за час')),
                ('date_of_change', models.DateTimeField(auto_now_add=True)),
                ('id_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель')),
            ],
            options={
                'verbose_name': 'Сумма',
                'verbose_name_plural': 'Зарплата',
                'ordering': ['-date_of_change', 'id_teacher'],
            },
        ),
    ]
