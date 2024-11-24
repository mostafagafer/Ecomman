from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard_view', views.dashboard_view, name='dashboard_view'),
    # path('price_view', views.price_view, name='price_view'),
    path('current_price', views.price, name='price'),
    path('performance_view/', views.performance_view, name='performance_view'),
    path('toggle_pin_table/<str:table_name>/', views.toggle_pin_table, name='toggle_pin_table'),
    path('current_price/', views.scrape_user_products_view, name='trigger_scrape_for_user_products'),


    # path('', views.dashboard_view, name='dashboard'),
]