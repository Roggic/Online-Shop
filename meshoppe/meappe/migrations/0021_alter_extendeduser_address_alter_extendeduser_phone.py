# Generated by Django 4.1.2 on 2022-12-20 18:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meappe', '0020_extendeduser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extendeduser',
            name='address',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='extendeduser',
            name='phone',
            field=models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Телефон должен быть в формате +71234567890', regex='^\\+?\\d{9,15}$')], verbose_name='Телефон'),
        ),
    ]
