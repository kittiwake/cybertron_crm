# Generated by Django 4.0.5 on 2022-07-17 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0006_alter_client_options_alter_client_guardian_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacherjournal',
            name='number_hours',
            field=models.DecimalField(decimal_places=1, default=2, max_digits=1, verbose_name='Количество часов'),
        ),
        migrations.CreateModel(
            name='VisitFix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('reserv', models.BooleanField(verbose_name='Запланирован')),
                ('visit', models.BooleanField(verbose_name='Посетил')),
                ('id_branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.branch', verbose_name='Филиал')),
                ('id_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.client', verbose_name='Ученик')),
                ('id_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.course', verbose_name='Предмет')),
                ('payed', models.ForeignKey(on_delete=models.SET(False), to='journal.paying', verbose_name='Дата оплаты')),
            ],
        ),
    ]
