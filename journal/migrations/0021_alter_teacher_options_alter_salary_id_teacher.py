# Generated by Django 4.2.1 on 2023-06-04 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0020_alter_teacher_contact_alter_teacher_first_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ['last_name'], 'verbose_name': 'Преподаватель', 'verbose_name_plural': 'Преподаватели'},
        ),
        migrations.AlterField(
            model_name='salary',
            name='id_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.teacher', verbose_name='Преподаватель'),
        ),
    ]
