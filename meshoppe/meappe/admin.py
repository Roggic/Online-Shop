from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


# Register your models here.
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_html_photo')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    fields = ('name', 'img', 'get_html_photo')
    readonly_fields = ('get_html_photo',)

    def get_html_photo(self, object):
        if object.img:
            return mark_safe(f"<img src='{object.img.url}' width=80>")

    get_html_photo.short_description = 'Миниатюра'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_html_photo')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    fields = ('name', 'img', 'get_html_photo')
    readonly_fields = ('get_html_photo',)

    def get_html_photo(self, object):
        if object.img:
            return mark_safe(f"<img src='{object.img.url}' width=80>")

    get_html_photo.short_description = 'Миниатюра'


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_html_photo')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    fields = ('name', 'img', 'get_html_photo')
    readonly_fields = ('get_html_photo',)

    def get_html_photo(self, object):
        if object.img:
            return mark_safe(f"<img src='{object.img.url}' width=80>")

    get_html_photo.short_description = 'Миниатюра'


class LocalizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'language',)
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    fields = ('language', 'img',)


class ProductAdmin(admin.ModelAdmin):
    # list_display = ('id', 'get_html_photo', 'name', 'price', 'in_stock', 'release_date', 'category')
    list_display = ('id', 'name', 'price', 'in_stock', 'release_date', 'category')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_editable = ('in_stock',)
    list_filter = ('in_stock', 'release_date', 'console', 'category', 'genre')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'price', 'description', 'in_stock', 'release_date',
              'console', 'category', 'genre', 'localization')
    # fields = ('name', 'slug', 'price', 'description', 'in_stock', 'img', 'get_html_photo', 'release_date',
    #           'console', 'category', 'genre', 'localization')
    # readonly_fields = ('get_html_photo',)
    save_on_top = True

    def get_html_photo(self, object):
        if object.img:
            return mark_safe(f"<img src='{object.img.url}' width=80>")

    get_html_photo.short_description = 'Миниатюра'


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_html_photo', 'image', 'order', 'product')
    list_display_links = ('id', 'get_html_photo', 'image')
    list_filter = ('product',)
    fields = ('image', 'product', 'order', 'get_html_photo')
    readonly_fields = ('get_html_photo',)

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=80>")

    get_html_photo.short_description = 'Миниатюра'


admin.site.register(Console, ConsoleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Localization, LocalizationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)


admin.site.site_title = 'Админ панель магазина MeShoppe'
admin.site.site_header = 'Админ панель магазина MeShoppe'
