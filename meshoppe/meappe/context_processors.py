from django.db.models import Q, Count

from .models import OrderDetails, Category
from .views import get_active_order, ProductFilter


def cart_count_cp(request):
    """Количество товаров в корзине"""
    user = request.user
    if user.is_authenticated:
        active_order = get_active_order(user)
        if active_order:
            order_details = OrderDetails.objects.filter(order=active_order)
            return {'cart_count': order_details.count()}
        else:
            return {'cart_count': 0}
    else:
        return {'cart_count': 0}


def categories_cp(request):
    q = Category.objects.filter(product__in_stock=True)\
        .annotate(count=Count('product'))
    return {'categories': q}


def product_filter(request):
    filter = ProductFilter(request.GET)
    return {'filter': filter}
