# Generated by Django 4.1.2 on 2022-11-28 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meappe', '0014_alter_image_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='img',
        ),
    ]