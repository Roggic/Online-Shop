import django_filters
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
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
                 for i in distinct_values(field='localization', field_related='language').exclude(
                localization__language__isnull=True)],
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
    paginate_by = 8
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
        filter = ProductFilter(self.request.GET, queryset)
        images = Image.objects.filter(product__in_stock=True)
        for product in filter.qs:
            product.images = images.filter(product_id=product.id)
        # queryset = super().get_queryset()
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
        context['images'] = Image.objects.filter(product=self.object)
        context['consoles'] = Console.objects.filter(products=self.object)
        context['genres'] = Genre.objects.filter(products=self.object)
        context['localizations'] = Localization.objects.filter(products=self.object)
        return dict(list(context.items()))


# class AddProduct(CreateView):
#     form_class = ProductForm
#     template_name = 'meappe/product_form.html'
#     success_url = reverse_lazy('shop')
#     raise_exception = True
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return dict(list(context.items()))

class UpdateProduct(UpdateView):
    model = Product
    form_class = ProductForm
    context_object_name = 'product'


class DeleteProduct(DeleteView):
    model = Product
    success_url = reverse_lazy('shop')


def add_product(request):
    ImageFormSet = formset_factory(ImageForm)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if all([form.is_valid(), formset.is_valid()]):
            product = form.save()
            max_order = get_order_num(product)
            for img_file in request.FILES.getlist('form-0-image'):
                image_obj = Image()
                image_obj.image = img_file
                image_obj.product = product
                image_obj.order = max_order
                image_obj.save()
                max_order += 1
            return redirect('product', product.slug)
    else:
        form = ProductForm()
        formset = ImageFormSet()
    return render(request, 'meappe/product_form.html', {'form': form, 'formset': formset})


def update_product(request, pk):
    ImageFormSet = formset_factory(ImageForm)
    queryset = Image.objects.filter(product=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=Product.objects.get(pk=pk))
        formset = ImageFormSet(request.POST, request.FILES)
        if all([form.is_valid(), formset.is_valid()]):
            product = form.save()

            # Удаляю удаленные фото
            images_to_delete = request.POST.getlist('images-delete')
            for i in images_to_delete:
                Image.objects.get(pk=int(i)).delete()

            # Сохраняю новый порядок фото
            new_order = request.POST.getlist('images-order')
            new_order_dict = make_new_order(new_order)
            for i in queryset:
                if str(i.id) in new_order:
                    i.order = new_order_dict[str(i.id)] * 100
            Image.objects.bulk_update(queryset, ['order'])
            for i in queryset:
                if str(i.id) in new_order:
                    i.order /= 100
                    i.order = int(i.order)
            Image.objects.bulk_update(queryset, ['order'])

            # Добавляю новые фото
            max_order = get_order_num(product)
            for img_file in request.FILES.getlist('form-0-image'):
                image_obj = Image()
                image_obj.image = img_file
                image_obj.product = product
                image_obj.order = max_order
                image_obj.save()
                max_order += 1

            return redirect('product', product.slug)
    else:
        form = ProductForm(instance=Product.objects.get(pk=pk))
        formset = ImageFormSet()

    return render(request, 'meappe/product_form.html', {'form': form, 'formset': formset, 'images': queryset})

    # def update_product(request, pk):
    # ImageFormSet = modelformset_factory(Image, fields={'image'}, extra=1,
    #                                     widgets={
    #                                         'image': forms.ClearableFileInput(attrs={'multiple': True,
    #                                                                                  'accept': 'image/jpeg, image/png, image/webp'}),
    #                                     })
    # # ImageFormSet = inlineformset_factory(Product, Image, fields=('image',))
    # queryset = Image.objects.filter(product=pk)
    # if request.method == 'POST':
    #     form = ProductForm(request.POST, instance=Product.objects.get(pk=pk))
    #     formset = ImageFormSet(request.POST, request.FILES, queryset=queryset)
    #     print(request.FILES)
    #     if all([form.is_valid(), formset.is_valid()]):
    #         product = form.save()
    #         for img_file in request.FILES.getlist('form-0-image'):
    #             image_obj = Image()
    #             image_obj.image = img_file
    #             image_obj.product = product
    #             image_obj.save()
    #         # for inline_form in formset:
    #         #     if inline_form.cleaned_data:
    #         #         image = inline_form.save(commit=False)
    #         #         image.product = product
    #         #         image.save()
    #         return redirect('shop')
    #
    # else:
    #     form = ProductForm(instance=Product.objects.get(pk=pk))
    #     formset = ImageFormSet(queryset=queryset)
    #
    # return render(request, 'meappe/product_form.html', {'form': form, 'formset': formset})


def test(request):
    return render(request, 'meappe/test.html')
