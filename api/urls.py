from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('products/popular/', popular_products_view),
    path('products/limited/', limited_products_view),
    path('product/<int:id>/', product_detail_view),
    path('product/<int:product_id>/reviews/', product_reviews_view),
    path('catalog/', catalog_view),
    path('basket/', basket_view),
    path('orders/<int:order_id>/', specific_order_view),
    path('orders/', orders_view),
    path('payment/<int:order_id>/', payment_view),
]
