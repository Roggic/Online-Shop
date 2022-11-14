from django.urls import path

from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('cart', cart, name='cart'),
    path('checkout', checkout, name='checkout'),
    path('contact', contact, name='contact'),
    path('product/<slug:product_slug>', ProductPage.as_view(), name='product'),
    path('shop', ShopPage.as_view(), name='shop'),
]
