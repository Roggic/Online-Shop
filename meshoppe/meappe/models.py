from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Q
from django.urls import reverse
from slugify import slugify
from django.core.validators import RegexValidator


# Чтобы PyCharm не подчеркивал objects в MyClass.objects.filter
class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class ExtendedUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?\d{9,15}$', message='Телефон должен быть в формате +71234567890')
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name='Телефон')
    address = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Адрес')


class Console(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/consoles', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Консоль'
        verbose_name_plural = 'Консоли'
        ordering = ['name']


class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/categories', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Genre(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='icons/genres', null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Localization(BaseModel):
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


class Product(BaseModel):
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


class Image(BaseModel):
    image = models.ImageField(upload_to='photos/', null=True, blank=True, verbose_name='Фото')
    product = models.ForeignKey(to='Product', null=True, blank=True, on_delete=models.CASCADE, verbose_name='Товар')
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


class Order(BaseModel):
    STATUS_CHOICES = (
        ('Создан', 'Создан'),
        ('Оформлен', 'Оформлен'),
        ('Подтвержден', 'Подтвержден'),
        ('В обработке', 'В обработке'),
        ('Отправлен', 'Отправлен'),
        ('Доставлен', 'Доставлен'),
        ('Отменен', 'Отменен'),
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name='Клиент')
    status = models.CharField(max_length=300, choices=STATUS_CHOICES, verbose_name='Статус')
    paid = models.BooleanField(default=False, verbose_name='Оплачен')
    datetime = models.DateTimeField(verbose_name='Дата и время')

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-datetime']


class OrderDetails(BaseModel):
    order = models.ForeignKey(to='Order', null=True, on_delete=models.SET_NULL, verbose_name='Заказ')
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.IntegerField(verbose_name='Цена')
    quantity = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.order} | {self.product}'

    class Meta:
        verbose_name = 'Детали заказа'
        verbose_name_plural = 'Детали заказов'
        ordering = ['-id']
