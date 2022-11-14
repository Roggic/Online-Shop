# Generated by Django 4.1.2 on 2022-11-09 17:26

from django.db import migrations, models
import meappe.models


class Migration(migrations.Migration):

    dependencies = [
        ('meappe', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name'], 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='console',
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to=meappe.models.img_path, verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='product',
            name='release_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выхода'),
        ),
    ]
