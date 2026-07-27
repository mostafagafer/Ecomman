from celery import shared_task


def _scraper_disabled_result(task_name):
    return {
        "status": "disabled",
        "task": task_name,
        "message": "Legacy scraper is backed up. Scrapling/LLM scraper is not active yet.",
        "records_created": 0,
    }


@shared_task
def scheduled_products_scraper(sample_size=200):
    return _scraper_disabled_result("scheduled_products_scraper")


@shared_task
def scheduled_bulk_scraper(sample_size=200):
    return _scraper_disabled_result("scheduled_bulk_scraper")


@shared_task
def scrape_user_products_task(product_ids):
    return _scraper_disabled_result("scrape_user_products_task")


@shared_task
def scrape_user_Bulk_product_task(product_ids):
    return _scraper_disabled_result("scrape_user_Bulk_product_task")
