from django.urls import path
from . import views

app_name = 'shop'  # Это пространство имен, чтобы не путать URL'ы разных приложений

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
]