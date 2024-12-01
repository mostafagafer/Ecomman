from celery import shared_task
from django.core.cache import cache
from django.contrib.auth.models import User
from client_profile.models import Profile
from scrapper.models import ScrapedData, ScrapedBulkData
from dashboard.utils import process_data  # Reuse the existing process function
import json


# Scheduled tasks
@shared_task
def caching_data():
    """
    Task to cache data for all users.
    """
    try:
        users = User.objects.all()
        for user in users:
            profile = Profile.objects.filter(user=user).first()
            if not profile:
                continue  # Skip users without a profile
            
            # Get user's products
            profile_products = profile.products.prefetch_related(
                'accounts_id', 'brand', 'category', 'subcategory'
            ).select_related('brand', 'category', 'subcategory')

            # Fetch `scraped_data` and `scraped_bulk_data`
            scraped_data = ScrapedData.objects.filter(
                product__in=profile_products
            ).select_related('product').prefetch_related('product__accounts_id')

            categories = profile_products.values_list('category__name', flat=True).distinct()
            subcategories = profile_products.values_list('subcategory__name', flat=True).distinct()
            scraped_bulk_data = ScrapedBulkData.objects.filter(
                key_name__in=list(categories) + list(subcategories)
            )

            # Process and cache data
            cache_key = f'dashboard_data_{user.id}'
            data = process_data(scraped_data, scraped_bulk_data)
            serialized_data = json.dumps(data)  # Serialize to JSON for caching
            cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours

        return "Caching completed for all users."
    except Exception as e:
        return f"Error in caching_data task: {str(e)}"


# Trigerred tasks
@shared_task
def cache_user_data(user_id):
    """
    Task to pre-cache data for a specific user.
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

        # Get user's products
        user_products = profile.products.prefetch_related(
            'accounts_id', 'brand', 'category', 'subcategory'
        ).select_related('brand', 'category', 'subcategory')

        # Fetch `scraped_data` and `scraped_bulk_data`
        scraped_data = ScrapedData.objects.filter(
            product__in=user_products
        ).select_related('product')

        categories = user_products.values_list('category__name', flat=True).distinct()
        subcategories = user_products.values_list('subcategory__name', flat=True).distinct()
        scraped_bulk_data = ScrapedBulkData.objects.filter(
            key_name__in=list(categories) + list(subcategories)
        )

        # Process and cache data
        cache_key = f'dashboard_data_{user.id}'
        data = process_data(scraped_data, scraped_bulk_data)
        serialized_data = json.dumps(data)
        cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours
        return f"Cached data for user {user.username}."
    except Exception as e:
        return f"Error caching data for user {user_id}: {str(e)}"
