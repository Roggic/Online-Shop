# Generated by Django 4.1.2 on 2023-01-11 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meappe', '0021_alter_extendeduser_address_alter_extendeduser_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetails',
            name='price',
            field=models.IntegerField(default=1, verbose_name='Цена'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Создан', 'Создан'), ('Оформлен', 'Оформлен'), ('Подтвержден', 'Подтвержден'), ('В обработке', 'В обработке'), ('Отправлен', 'Отправлен'), ('Доставлен', 'Доставлен'), ('Отменен', 'Отменен')], max_length=300, verbose_name='Статус'),
        ),
    ]
