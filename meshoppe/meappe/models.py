from django.db import models
from django.urls import reverse

from transliterate import slugify


# Create your models here.
class Console(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/consoles', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Консоль'
        verbose_name_plural = 'Консоли'
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/categories', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/genres', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Localization(models.Model):
    language = models.CharField(max_length=255, unique=True, verbose_name='Язык')

    def __str__(self):
        return self.language

    class Meta:
        verbose_name = 'Локализация'
        verbose_name_plural = 'Локализации'
        ordering = ['language']


def img_path(instance, filename):
    text_en = slugify(f'{instance.category.name}')
    return f'images/{text_en}/{filename}'


class Product(models.Model):
    name = models.CharField(max_length=300, verbose_name='Название')
    slug = models.SlugField(max_length=300, unique=True, db_index=True, verbose_name='URL')
    price = models.FloatField(verbose_name='Цена')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    # img = models.ImageField(upload_to=img_path, null=True, blank=True, verbose_name='Фото')
    img = models.ManyToManyField(to='Image', related_name='products', blank=True, verbose_name='Фото')
    release_date = models.DateField(null=True, blank=True, verbose_name='Дата выхода')
    console = models.ManyToManyField(to='Console', related_name='products', blank=True, verbose_name='Консоли')
    category = models.ForeignKey(to='Category', null=True, blank=True, on_delete=models.PROTECT,
                                 verbose_name='Категория')
    genre = models.ManyToManyField(to='Genre', related_name='products', blank=True, verbose_name='Жанры')
    localization = models.ManyToManyField(to='Localization', related_name='products', blank=True,
                                          verbose_name='Локализация')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']


class Image(models.Model):
    image = models.ImageField(upload_to='photos/', null=True, blank=True, verbose_name='Фото')
    product = models.ForeignKey(to='Product', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'

