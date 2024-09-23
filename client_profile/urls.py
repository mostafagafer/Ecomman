from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
# from .views import PromoPlanCreateView, PromoPlanUpdateView, promo_plan_list

app_name= 'client_profile'

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('edit', views.profile_edit, name='profile_edit'),
    path('products/', views.profile_products, name='profile_products'),
    path('products/create/', views.product_create, name='product_create'),
    # # path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    # path('product/<int:id>/edit/', views.product_edit, name='product_edit'),

    # path('products/create/', views.product_create_or_edit, name='product_create'),
    # path('products/edit/<int:id>/', views.product_edit, name='product_edit'),
    # path('products/detail/<int:id>/', views.product_detail, name='product_detail'),

    # path('products/form/', views.product_form, name='product_form'),
    # path('add_account/', views.product_form, name='add_account'),
    # path('remove_account/', views.product_form, name='remove_account'),
    path('promo-plans/', views.promo_plan_list, name='promo_plan_list'),
    # path('promo-plan/create/', PromoPlanCreateView.as_view(), name='create_promo_plan'),
    # path('promo-plan/<int:pk>/edit/', PromoPlanUpdateView.as_view(), name='edit_promo_plan'),
    path('promo-plan/create/', views.create_or_edit_promo_plan, name='create_promo_plan'),
    path('promo-plan/<int:pk>/edit/', views.create_or_edit_promo_plan, name='edit_promo_plan'),
    path('promo-plan/<int:pk>/remove/', views.remove_promo_plan, name='remove_promo_plan'),  # Add this line


]

