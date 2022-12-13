from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Q
from django.urls import reverse
from slugify import slugify


# from transliterate import slugify


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
    slug = models.SlugField(allow_unicode=True, max_length=300, unique=True, db_index=True, verbose_name='URL')
    price = models.FloatField(verbose_name='Цена')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    # img = models.ImageField(upload_to=img_path, null=True, blank=True, verbose_name='Фото')  # Для одного фото
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.slug:
            slug_str = f'{self.name}'
            self.slug = slugify(slug_str)
        slug_exists = Product.objects.filter(~Q(id=self.id), slug=self.slug)
        if slug_exists.count() > 0:
            self.slug = f'{self.slug}-2'
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']


def validate_file_extension(value):
    types = ['image/jpeg', 'image/png', 'image/webp']
    if value.file.content_type not in types:
        raise ValidationError(u'Неверный формат файла, нужны: jpg, png, webp')


def get_order_num(product):
    max_order = Image.objects.filter(product_id=product) \
        .aggregate(Max('order'))
    if max_order['order__max'] is None:
        max_order['order__max'] = 0
    return max_order['order__max'] + 1


def make_new_order(lst):
    return {f'{v}': i + 1 for i, v in enumerate(lst)}


class Image(models.Model):
    image = models.ImageField(upload_to='photos/', null=True, blank=True, verbose_name='Фото')
    product = models.ForeignKey(to='Product', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name='Порядок')

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'
        ordering = ['product', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'order'],
                name='unique_product_order',
            )
        ]
