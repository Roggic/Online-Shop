import django_filters
from django import forms
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView
from django_filters import OrderingFilter
from django_filters.widgets import RangeWidget

from .forms import *
from .models import *


def home(request):
    return render(request, 'meappe/index.html')


def cart(request):
    return render(request, 'meappe/cart.html')


def checkout(request):
    return render(request, 'meappe/checkout.html')


def contact(request):
    return render(request, 'meappe/contact.html')


def distinct_values(field, field_related='name'):
    """Возвращает уникальные значения поля, для которого есть товары.
    field - поле из Product;
    field_related - поле из связанной таблицы.
    Функция может возвращать с None значениями - их придется исключать вне этой функции.
    """
    full_related = f'{field}__{field_related}'
    distinct_choices = Product.objects.values(f'{field}__id', full_related) \
        .distinct(full_related).order_by(full_related)
    return distinct_choices


class ProductFilter(django_filters.FilterSet):
    category = django_filters.MultipleChoiceFilter(
        choices=[(i['category__id'], i['category__name'])
                 for i in distinct_values(field='category').exclude(category__name__isnull=True)],
        widget=forms.CheckboxSelectMultiple)

    console = django_filters.MultipleChoiceFilter(
        choices=[(i['console__id'], i['console__name'])
                 for i in distinct_values(field='console').exclude(console__name__isnull=True)],
        widget=forms.CheckboxSelectMultiple)

    price = django_filters.RangeFilter(field_name='price', label='Цена',
                                       widget=RangeWidget(attrs={'placeholder': '0', 'class': 'short-width'}))

    genre = django_filters.MultipleChoiceFilter(
        choices=[(i['genre__id'], i['genre__name'])
                 for i in distinct_values(field='genre').exclude(genre__name__isnull=True)],
        widget=forms.CheckboxSelectMultiple)

    localization = django_filters.MultipleChoiceFilter(
        choices=[(i['localization__id'], i['localization__language'])
                 for i in distinct_values(field='localization', field_related='language').exclude(localization__language__isnull=True)],
        widget=forms.CheckboxSelectMultiple)

    sort = OrderingFilter(fields=(('price', 'price'), ('release_date', 'release_date')),
                          field_labels={'price': 'по цене', 'release_date': 'по дате выхода'}, label='Сортировать')

    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'console': ['exact'],
            'genre': ['exact'],
            'localization': ['exact'],
        }


class ShopPage(ListView):
    paginate_by = 6
    model = Product
    template_name = 'meappe/shop.html'
    context_object_name = 'products'
    ordering = ['-release_date']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        filter = ProductFilter(self.request.GET, queryset)
        context['filter'] = filter
        # context['current_order'] = self.get_ordering()
        # context['order'] = self.order
        return dict(list(context.items()))

    def get_queryset(self):
        queryset = Product.objects.filter(in_stock=True)
        # queryset = super().get_queryset()
        filter = ProductFilter(self.request.GET, queryset)
        return filter.qs

    # def get_ordering(self):
    # Сортировка
    #     self.order = self.request.GET.get('order', 'asc')
    #     ordering = self.request.GET.get('ordering', 'release_date')
    #     if self.order == 'desc':
    #         ordering = f'-{ordering}'
    #     return ordering


class ProductPage(DetailView):
    model = Product
    template_name = 'meappe/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['consoles'] = Console.objects.filter(products=self.object)
        context['genres'] = Genre.objects.filter(products=self.object)
        context['localizations'] = Localization.objects.filter(products=self.object)
        return dict(list(context.items()))
