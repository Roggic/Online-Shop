from django.contrib.auth.views import PasswordChangeView
from django.urls import path, re_path, include

from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('shop', ShopPage.as_view(), name='shop'),
    path('product/<slug:product_slug>', ProductPage.as_view(), name='product'),
    path('shop/add_product', add_product, name='add_product'),
    path('shop/<int:pk>/update', update_product, name='update_product'),
    path('shop/<int:pk>/delete/', DeleteProduct.as_view(), name='delete_product'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    re_path(r'^accounts/update/(?P<slug>[\-\w]+)/$', update_account, name='update_account'),
    path('accounts/password_change/', PasswordChangeView.as_view(template_name='meappe/account.html'), name='password_change'),
    path('accounts/password_change/done', LoginUser.as_view(), name='password_change_done'),
    path('cart', cart, name='cart'),
    path('checkout', checkout, name='checkout'),
    path('contact', contact, name='contact'),
    # path('addproduct', AddProduct.as_view(), name='add_product'),
    # path('shop/<int:pk>/update/', UpdateProduct.as_view(), name='update_product'),
]
