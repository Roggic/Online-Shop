import django_filters
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import modelformset_factory, inlineformset_factory
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django_filters import OrderingFilter
from django_filters.widgets import RangeWidget
from django.contrib.auth import logout, login
from django.core.exceptions import ObjectDoesNotExist

from .forms import *
from .models import *


def home(request):
    queryset = Product.objects.filter(in_stock=True)[:8]
    images = Image.objects.filter(product__in_stock=True)
    for product in queryset:
        product.images = images.filter(product_id=product.id)
    return render(request, 'meappe/index.html', {'featured': queryset})


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
    # category = django_filters.MultipleChoiceFilter(
    #     choices=[(i['category__id'], i['category__name'])
    #              for i in distinct_values(field='category').exclude(category__name__isnull=True)],
    #     widget=forms.CheckboxSelectMultiple)
    #
    # console = django_filters.MultipleChoiceFilter(
    #     choices=[(i['console__id'], i['console__name'])
    #              for i in distinct_values(field='console').exclude(console__name__isnull=True)],
    #     widget=forms.CheckboxSelectMultiple)
    #
    # genre = django_filters.MultipleChoiceFilter(
    #     choices=[(i['genre__id'], i['genre__name'])
    #              for i in distinct_values(field='genre').exclude(genre__name__isnull=True)],
    #     widget=forms.CheckboxSelectMultiple)
    #
    # localization = django_filters.MultipleChoiceFilter(
    #     choices=[(i['localization__id'], i['localization__language'])
    #              for i in distinct_values(field='localization', field_related='language').exclude(
    #             localization__language__isnull=True)],
    #     widget=forms.CheckboxSelectMultiple)
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)
    console = django_filters.ModelMultipleChoiceFilter(queryset=Console.objects.all(), widget=forms.CheckboxSelectMultiple)
    genre = django_filters.ModelMultipleChoiceFilter(queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple)
    localization = django_filters.ModelMultipleChoiceFilter(queryset=Localization.objects.all(), widget=forms.CheckboxSelectMultiple)

    price = django_filters.RangeFilter(field_name='price', label='Цена',
                                       widget=RangeWidget(attrs={'placeholder': '0', 'class': 'short-width'}))

    sort = OrderingFilter(fields=(('price', 'price'), ('release_date', 'release_date')),
                          field_labels={'price': 'по цене', 'release_date': 'по дате выхода'}, label='Сортировать')

    name = django_filters.CharFilter(lookup_expr='icontains', label='Поиск',
                                     widget=forms.TextInput(attrs={'placeholder': 'Найти...', 'class': 'form-control'}))

    class Meta:
        model = Product
        fields = ['category', 'console', 'genre', 'localization']


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


def get_active_order(user):
    active_order = Order.objects.filter(Q(user=user), Q(status='Создан'))
    return active_order[0] if active_order else False


class ProductPage(DetailView, FormMixin):
    model = Product
    template_name = 'meappe/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    form_class = CartForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Image.objects.filter(product=self.object)
        context['consoles'] = Console.objects.filter(products=self.object)
        context['genres'] = Genre.objects.filter(products=self.object)
        context['localizations'] = Localization.objects.filter(products=self.object)
        return dict(list(context.items()))

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            slug = self.kwargs.get(self.slug_url_kwarg, None)
            updated_request = request.POST.copy()
            product = Product.objects.get(slug=slug)
            quantity = int(updated_request['quantity'])
            updated_request.update({'product': product})
            updated_form = CartForm(updated_request)
            if updated_form.is_valid():
                # Логика добавления товара в корзину
                active_order = get_active_order(user)
                if active_order:  # Если заказ есть
                    order_details = OrderDetails.objects.filter(Q(order=active_order), Q(product=product))
                    if order_details.count() > 0:  # Если товар в корзине
                        # Увеличить количество
                        product_in_order = order_details[0]
                        product_in_order.quantity += quantity
                        product_in_order.save()
                    else:
                        # Добавить к заказу
                        new_order_detail = OrderDetails(order=active_order, product=product,
                                                        price=product.price, quantity=quantity)
                        new_order_detail.save()
                else:
                    # Создать заказ
                    new_order = Order(user=user, status='Создан', paid=False, datetime=datetime.now())
                    new_order.save()
                    # Добавить к заказу
                    new_order_detail = OrderDetails(order=new_order, product=product,
                                                    price=product.price, quantity=quantity)
                    new_order_detail.save()

            return HttpResponseRedirect(self.request.path_info)
        else:
            return redirect('login')


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


class DeleteProduct(DeleteView):
    model = Product
    success_url = reverse_lazy('shop')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'meappe/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'meappe/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


def update_account(request, slug):
    user = User.objects.get(username=slug)
    try:
        extended_user = ExtendedUser.objects.get(user=user.id)
    except ObjectDoesNotExist:
        extended_user = ExtendedUser(user=user, phone='', address='')

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        form2 = ExtendedUserForm(request.POST, instance=extended_user)
        if all([form.is_valid(), form2.is_valid()]):
            form.save()
            form2.save()
            return redirect('update_account', slug)
    else:
        form = UserForm(instance=user)
        form2 = ExtendedUserForm(instance=extended_user)
    return render(request, 'meappe/account.html', {'form': form, 'form2': form2})


def cart(request):
    current_user = request.user
    CartFormSet = modelformset_factory(OrderDetails, CartForm, extra=0, can_delete=True)
    queryset = OrderDetails.objects.filter(Q(order__user=current_user), Q(order__status='Создан'))
    images = Image.objects.filter(product__in_stock=True)
    for product in queryset:
        product.images = images.filter(product_id=product.product.id).first()

    if current_user.is_authenticated:
        if request.method == 'POST':
            formset = CartFormSet(request.POST, queryset=queryset)
            if formset.is_valid():
                formset.save()
                return redirect('checkout')
        else:
            formset = CartFormSet(queryset=queryset)
            return render(request, 'meappe/cart.html', {'formset': formset})
    else:
        return render(request, 'meappe/cart.html')


def checkout(request):
    user = request.user
    try:
        extended_user = ExtendedUser.objects.get(user=user.id)
    except ObjectDoesNotExist:
        extended_user = ExtendedUser(user=user, phone='', address='')

    order_details = OrderDetails.objects.filter(Q(order__user=user), Q(order__status='Создан'))
    images = Image.objects.filter(product__in_stock=True)
    for product in order_details:
        product.images = images.filter(product_id=product.product.id).first()

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        form2 = ExtendedUserForm(request.POST, instance=extended_user)
        payment = PaymentForm(request.POST)
        if all([form.is_valid(), form2.is_valid(), payment.is_valid()]):
            form.save()
            form2.save()
            return redirect('order_confirmed')
    else:
        form = UserForm(instance=user)
        form2 = ExtendedUserForm(instance=extended_user)
        payment = PaymentForm()

    return render(request, 'meappe/checkout.html', {'form': form, 'form2': form2,
                                                    'order_details': order_details, 'payment': payment})


def order_confirmed(request):
    user = request.user
    active_order = get_active_order(user)
    active_order.status = 'Оформлен'
    active_order.save()
    return render(request, 'meappe/order_confirmed.html')


class OrdersHistory(ListView):
    paginate_by = 5
    model = Order
    template_name = 'meappe/orders_history.html'
    context_object_name = 'orders'
    ordering = ['-datetime']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()
        order_details = OrderDetails.objects.filter(order__user=self.request.user)
        products = [order_detail.product for order_detail in order_details]
        images = Image.objects.filter(product__in=products)
        for order in orders:
            order.order_details = order_details.filter(order=order)
            order.sum = 0
            for order_detail in order.order_details:
                order_detail.image = images.filter(product_id=order_detail.product.id).first()
                order.sum += order_detail.price * order_detail.quantity

        context['orders'] = orders
        context['order_details'] = order_details
        context['images'] = images
        return dict(list(context.items()))

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


def contact(request):
    return render(request, 'meappe/contact.html')

# class AddProduct(CreateView):
#     form_class = ProductForm
#     template_name = 'meappe/product_form.html'
#     success_url = reverse_lazy('shop')
#     raise_exception = True
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return dict(list(context.items()))

# class UpdateProduct(UpdateView):
#     model = Product
#     form_class = ProductForm
#     context_object_name = 'product'
#
#
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
