from celery import shared_task
from django.core.cache import cache
from django.contrib.auth.models import User
from client_profile.models import Profile
from scrapper.models import ScrapedData, ScrapedBulkData
from dashboard.utils import process_data  # Reuse the existing process function
import json
# from datetime import datetime


# Scheduled tasks
# @shared_task
# def caching_data():
#     """
#     Task to cache data for all users.
#     """
#     try:
#         users = User.objects.all()
#         for user in users:
#             profile = Profile.objects.filter(user=user).first()
#             if not profile:
#                 continue  # Skip users without a profile
            
#             # Get user's products
#             profile_products = profile.products.prefetch_related(
#                 'accounts_id', 'brand', 'category', 'subcategory'
#             ).select_related('brand', 'category', 'subcategory')

#             # Fetch `scraped_data` and `scraped_bulk_data`
#             scraped_data = ScrapedData.objects.filter(
#                 product__in=profile_products
#             ).select_related('product').prefetch_related('product__accounts_id')

#             categories = profile_products.values_list('category__name', flat=True).distinct()
#             subcategories = profile_products.values_list('subcategory__name', flat=True).distinct()
#             scraped_bulk_data = ScrapedBulkData.objects.filter(
#                 key_name__in=list(categories) + list(subcategories)
#             )

#             # Process and cache data
#             cache_key = f'dashboard_data_{user.id}'
#             data = process_data(scraped_data, scraped_bulk_data)
#             serialized_data = json.dumps(data)  # Serialize to JSON for caching
#             cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours

#         return "Caching completed for all users."
#     except Exception as e:
#         return f"Error in caching_data task: {str(e)}"


# Trigerred tasks
# @shared_task
# def cache_user_data(user_id):
#     """
#     Task to pre-cache data for a specific user.
#     """
#     from django.contrib.auth.models import User
#     try:
#         user = User.objects.get(id=user_id)
#         profile = Profile.objects.get(user=user)

#         # Get user's products
#         user_products = profile.products.prefetch_related(
#             'accounts_id', 'brand', 'category', 'subcategory'
#         ).select_related('brand', 'category', 'subcategory')

#         # Fetch `scraped_data` and `scraped_bulk_data`
#         scraped_data = ScrapedData.objects.filter(
#             product__in=user_products
#         ).select_related('product')

#         categories = user_products.values_list('category__name', flat=True).distinct()
#         subcategories = user_products.values_list('subcategory__name', flat=True).distinct()
#         scraped_bulk_data = ScrapedBulkData.objects.filter(
#             key_name__in=list(categories) + list(subcategories)
#         )

#         # Process and cache data
#         cache_key = f'dashboard_data_{user.id}'
#         data = process_data(scraped_data, scraped_bulk_data)
#         serialized_data = json.dumps(data)
#         cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours
#         return f"Cached data for user {user.username}."
#     except Exception as e:
#         return f"Error caching data for user {user_id}: {str(e)}"


# @shared_task
# def cache_user_data(user_id):
#     """
#     Task to pre-cache data for a specific user.
#     """
#     from django.contrib.auth.models import User
#     import logging
#     logger = logging.getLogger(__name__)
    
#     try:
#         user = User.objects.get(id=user_id)
#         profile = Profile.objects.get(user=user)

#         # Get user's products
#         user_products = profile.products.prefetch_related(
#             'accounts_id', 'brand', 'category', 'subcategory'
#         ).select_related('brand', 'category', 'subcategory')

#         # Fetch `scraped_data` and `scraped_bulk_data`
#         scraped_data = ScrapedData.objects.filter(
#             product__in=user_products
#         ).select_related('product')

#         categories = user_products.values_list('category__name', flat=True).distinct()
#         subcategories = user_products.values_list('subcategory__name', flat=True).distinct()
#         scraped_bulk_data = ScrapedBulkData.objects.filter(
#             key_name__in=list(categories) + list(subcategories)
#         )

#         # Debug: Log input data counts
#         logger.info(f"User {user_id}: {scraped_data.count()} scraped_data, {scraped_bulk_data.count()} scraped_bulk_data")

#         # Process and cache data
#         cache_key = f'dashboard_data_{user.id}'
#         try:
#             data = process_data(scraped_data, scraped_bulk_data)
#         except Exception as process_error:
#             logger.error(f"Error in process_data for user {user_id}: {process_error}")
#             raise

#         serialized_data = json.dumps(data)
#         cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours
#         return f"Cached data for user {user.username}."
#     except Exception as e:
#         logger.error(f"Error caching data for user {user_id}: {str(e)}")
#         return f"Error caching data for user {user_id}: {str(e)}"




# @shared_task
# def cache_user_data(user_id):
#     """
#     Task to pre-cache data for a specific user.
#     """
#     from django.contrib.auth.models import User
#     import logging
#     logger = logging.getLogger(__name__)
#     from datetime import datetime

#     try:
#         user = User.objects.get(id=user_id)
#         profile = Profile.objects.get(user=user)

#         # Get existing cached data if available
#         cache_key = f'dashboard_data_{user.id}'
#         existing_data = cache.get(cache_key)
#         if existing_data:
#             existing_data = json.loads(existing_data)
#             last_cached_at = max(existing_data.get('scraped_at', []), default=None)
#             if last_cached_at:
#                 last_cached_datetime = datetime.fromisoformat(last_cached_at)
#             else:
#                 last_cached_datetime = None
#         else:
#             existing_data = {key: [] for key in process_data([], []).keys()}
#             last_cached_datetime = None

#         # Debug: Log last cached time
#         logger.info(f"User {user_id}: Last cached at {last_cached_datetime}")

#         # Get user's products
#         user_products = profile.products.prefetch_related(
#             'accounts_id', 'brand', 'category', 'subcategory'
#         ).select_related('brand', 'category', 'subcategory')

#         # Filter `scraped_data` and `scraped_bulk_data` by time
#         scraped_data = ScrapedData.objects.filter(product__in=user_products).select_related('product')
#         if last_cached_datetime:
#             scraped_data = scraped_data.filter(scraped_at__gt=last_cached_datetime)

#         categories = user_products.values_list('category__name', flat=True).distinct()
#         subcategories = user_products.values_list('subcategory__name', flat=True).distinct()
#         scraped_bulk_data = ScrapedBulkData.objects.filter(
#             key_name__in=list(categories) + list(subcategories)
#         )
#         if last_cached_datetime:
#             scraped_bulk_data = scraped_bulk_data.filter(scraped_at__gt=last_cached_datetime)

#         # Debug: Log input data counts after filtering
#         logger.info(
#             f"User {user_id}: {scraped_data.count()} new `scraped_data`, "
#             f"{scraped_bulk_data.count()} new `scraped_bulk_data`"
#         )

#         # Check if there's any data to process
#         if not scraped_data.exists() and not scraped_bulk_data.exists():
#             logger.warning(f"No new data to process for user {user_id}.")
#             return f"No new data to process for user {user.username}."

#         # Process new data
#         new_data = process_data(scraped_data, scraped_bulk_data)

#         # Append new data to existing cached data
#         for key, values in new_data.items():
#             existing_data[key].extend(values)

#         # Save updated data to cache
#         serialized_data = json.dumps(existing_data)
#         cache.set(cache_key, serialized_data, timeout=86400.0)  # Cache for 24 hours

#         return f"Cached data for user {user.username}."
#     except Exception as e:
#         logger.error(f"Error caching data for user {user_id}: {str(e)}")
#         return f"Error caching data for user {user_id}: {str(e)}"

@shared_task
def cache_user_data(user_id):
    """
    Task to pre-cache data for a specific user.
    """
    from django.contrib.auth.models import User
    import logging
    import json
    from datetime import datetime
    from django.core.cache import cache

    logger = logging.getLogger(__name__)

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

        # Check if existing cached data is available
        cache_key = f'dashboard_data_{user.id}'
        existing_data = cache.get(cache_key)

        if existing_data:
            existing_data = json.loads(existing_data)
            last_cached_at = max(existing_data.get('scraped_at', []), default=None)
            last_cached_datetime = (
                datetime.fromisoformat(last_cached_at) if last_cached_at else None
            )
            logger.info(f"Last cached datetime for user {user_id}: {last_cached_datetime}")
        else:
            logger.info(f"No existing cache found for user {user_id}. Starting fresh.")
            last_cached_datetime = None
            existing_data = None

        # Apply time filters only if there is an existing cache
        if last_cached_datetime:
            scraped_data = scraped_data.filter(scraped_at__gt=last_cached_datetime)
            scraped_bulk_data = scraped_bulk_data.filter(scraped_at__gt=last_cached_datetime)

        logger.info(f"User {user_id}: {scraped_data.count()} scraped_data, {scraped_bulk_data.count()} scraped_bulk_data")

        # If no data is found after filtering, process all data (fresh cache scenario)
        if not last_cached_datetime or not scraped_data.exists() and not scraped_bulk_data.exists():
            logger.warning(f"No cached datetime or no new data found for user {user_id}. Processing all data.")
            scraped_data = ScrapedData.objects.filter(product__in=user_products)
            scraped_bulk_data = ScrapedBulkData.objects.filter(
                key_name__in=list(categories) + list(subcategories)
            )

        # Process and cache data
        try:
            new_data = process_data(scraped_data, scraped_bulk_data)

            # Append new data to existing data if it exists
            if existing_data:
                for key, values in new_data.items():
                    if key in existing_data:
                        existing_data[key].extend(values)  # Append new rows
                    else:
                        existing_data[key] = values  # Add new keys if not present
            else:
                existing_data = new_data  # Initialize with new data if no cache exists

            serialized_data = json.dumps(existing_data)  # Serialize the updated data
            cache.set(cache_key, serialized_data, timeout=None)  # Save to cache
            logger.info(f"Successfully cached and updated data for user {user.username}.")
            return f"Cached data for user {user.username}."
        except Exception as process_error:
            logger.error(f"Error in process_data for user {user_id}: {process_error}")
            raise
    except Exception as e:
        logger.error(f"Error caching data for user {user_id}: {str(e)}")
        return f"Error caching data for user {user_id}: {str(e)}"

@shared_task
def caching_data():
    """
    Task to pre-cache data for all users.
    """
    from django.contrib.auth.models import User
    import logging
    logger = logging.getLogger(__name__)

    try:
        users = User.objects.all()
        logger.info(f"Starting cache update for {users.count()} users.")

        for user in users:
            logger.info(f"Processing cache for user {user.username} (ID: {user.id}).")
            result = cache_user_data(user.id)
            logger.info(f"Result for user {user.username} (ID: {user.id}): {result}")

        return "Cache update completed for all users."
    except Exception as e:
        logger.error(f"Error during cache update for all users: {str(e)}")
        return f"Error during cache update for all users: {str(e)}"


