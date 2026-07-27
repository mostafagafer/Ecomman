from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name= 'client_profile'

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('edit', views.profile_edit, name='profile_edit'),
    path('products/', views.profile_products, name='profile_products'),
    path('products/create/', views.product_create, name='product_create'),
    path('product/<int:id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:id>/delete/', views.product_delete, name='product_delete'),
    path('products/detail/<int:id>/', views.product_detail, name='product_detail'),

    path('promo-plans/', views.promo_plan_list, name='promo_plan_list'),
    path('promo-plan/create/', views.create_or_edit_promo_plan, name='create_promo_plan'),
    path('promo-plan/<int:pk>/edit/', views.create_or_edit_promo_plan, name='edit_promo_plan'),
    path('promo-plan/<int:pk>/remove/', views.remove_promo_plan, name='remove_promo_plan'),  # Add this line


]

