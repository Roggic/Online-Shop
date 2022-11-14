from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView

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


class ShopPage(ListView):
    paginate_by = 6
    model = Product
    template_name = 'meappe/shop.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_queryset(self):
        return Product.objects.all()


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
