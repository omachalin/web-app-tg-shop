from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<uuid:pk>/', views.product_detail, name='product_detail'),
    path('search-product/', views.search_product_list, name='search-product'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
]
