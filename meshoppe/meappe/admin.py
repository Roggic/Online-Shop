from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import *


class ExtendedUserInline(admin.StackedInline):
    model = ExtendedUser
    can_delete = False
    verbose_name = 'Дополнительно'


class UserAdmin(BaseUserAdmin):
    inlines = (ExtendedUserInline, )


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
    fields = ('language',)


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


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'paid', 'datetime')
    list_display_links = ('id', )
    list_editable = ('status', 'paid',)
    search_fields = ('user', )
    fields = ('id', 'user', 'status', 'paid', 'datetime')
    readonly_fields = ('id', )


class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity')
    list_display_links = ('id', )
    search_fields = ('product', )
    fields = ('id', 'order', 'product', 'price', 'quantity')
    readonly_fields = ('id', )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Console, ConsoleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Localization, LocalizationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetails, OrderDetailsAdmin)

admin.site.site_title = 'Админ панель магазина MeShoppe'
admin.site.site_header = 'Админ панель магазина MeShoppe'
