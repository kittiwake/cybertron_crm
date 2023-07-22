# Generated by Django 4.0.5 on 2022-07-17 13:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0004_teacherjournal_time_of_visit_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=60)),
                ('name', models.CharField(max_length=60)),
                ('guardian', models.CharField(max_length=200)),
                ('mobile_phone', models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Enter a valid international mobile phone number starting with +(country code)', regex='^\\+(?:[0-9]●?){6,14}[0-9]$')], verbose_name='Mobile phone')),
            ],
        ),
    ]