from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # path('', views.dashboard, name='dashboard'),
    path('', views.index, name='index'),
    path('current_price', views.price, name='price'),
    # path('product-performance/', views.product_performance_view, name='product_performance_view'),
    # path('product-performance2/', views.product_performance_view, name='product_performance_view'),
    path('performance_view/', views.performance_view, name='performance_view'),
    path('toggle_pin_table/<str:table_name>/', views.toggle_pin_table, name='toggle_pin_table'),


    path('', views.dashboard_view, name='dashboard'),
]