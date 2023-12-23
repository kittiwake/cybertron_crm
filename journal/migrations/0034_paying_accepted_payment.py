# Generated by Django 4.2.1 on 2023-12-13 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0033_alter_client_tg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='paying',
            name='accepted_payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='journal.teacher', verbose_name='Принял'),
        ),
    ]
