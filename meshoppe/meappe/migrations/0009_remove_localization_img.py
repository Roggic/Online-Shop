# Generated by Django 4.1.2 on 2022-11-12 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meappe', '0008_category_img_console_img_genre_img_localization_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='localization',
            name='img',
        ),
    ]
