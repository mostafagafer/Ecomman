import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from pathlib import Path
# import os
# from environ import Env

# # Get path to .env (up from /dashboard to project root)
# BASE_DIR = Path(__file__).resolve().parent.parent
# ENV_PATH = BASE_DIR / "project/.env"


# # Load env file
# env = Env()
# if ENV_PATH.exists():
#     env.read_env(str(ENV_PATH))
# else:
#     print("❌ .env file not found!")
#     exit(1)

# # Try to read the variable
# try:
#     DATABASE_URL = env("DATABASE_URL")
# except Exception as e:
#     print("❌ Could not read DATABASE_URL:", e)


import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')



# Now you can access the settings
from django.conf import settings

# Access the DATABASE_URL from settings.py
DATABASE_URL = settings.DATABASE_URL


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Extract Supabase URL from environment variables
# "postgresql://postgres.rcbqpbokrxozbislevtb:Ecomman_123@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    raise ValueError("DATABASE_URL environment variable not set")

# Use the Supabase URL directly for SQLAlchemy
DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://')
engine = create_engine(DATABASE_URI)

def setup_refresh_log_table():
    """Create a table to track materialized view refreshes"""
    try:
        with engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS materialized_view_refresh_log (
                    id SERIAL PRIMARY KEY,
                    view_name VARCHAR(255) NOT NULL,
                    refresh_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            logger.info("Refresh log table created or already exists")
    except Exception as e:
        logger.error(f"Error creating refresh log table: {e}")
        raise

def log_refresh(view_name, connection):
    """Log a refresh event for a materialized view"""
    try:
        connection.execute(text(f"""
            INSERT INTO materialized_view_refresh_log (view_name) 
            VALUES ('{view_name}');
        """))
        logger.info(f"Logged refresh for {view_name}")
    except Exception as e:
        logger.error(f"Error logging refresh for {view_name}: {e}")

def create_materialized_view(view_name, days):
    try:
        with engine.begin() as connection:
            connection.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name};"))
            logger.info(f"Dropped materialized view '{view_name}' if it existed.")
            
            sql = f"""
            CREATE MATERIALIZED VIEW {view_name} AS
            WITH competitor_refs AS (
                SELECT 
                    p.id AS product_id,
                    string_agg(cp."TITLE", ' | ') AS competitor_products
                FROM client_profile_product p
                LEFT JOIN client_profile_product_competitor_references cr ON p.id = cr.from_product_id
                LEFT JOIN client_profile_product cp ON cr.to_product_id = cp.id
                GROUP BY p.id
            ),
            latest_scraped_data AS (
                SELECT DISTINCT ON (sd.product_id, sd.scraped_at::date) 
                    sd.product_id,
                    sd.dawa_price, sd.dawa_discount,
                    sd.amazon_price, sd.amazon_discount,
                    sd.nahdi_price, sd.nahdi_discount,
                    sd.nahdi_ordered_qty,
                    sd.noon_sa_price, sd.noon_sa_discount,
                    sd.amazon_title, sd.nahdi_title, sd.noon_sa_title, sd.dawa_title,
                    sd.scraped_at::date AS scraped_date
                FROM scrapper_scrapeddata sd
                WHERE sd.scraped_at >= NOW() - INTERVAL '{days} days'
                ORDER BY sd.product_id, sd.scraped_at::date, sd.scraped_at DESC
            ),
            combined_data AS (
                SELECT
                    p."TITLE" AS product_name,
                    p.category_id,
                    COALESCE(c.name, 'Unknown') AS category_name,
                    p.subcategory_id,
                    COALESCE(sc.name, 'Unknown') AS subcategory_name,
                    p."RSP_VAT" AS rsp_vat,
                    p.is_competitor,
                    cr.competitor_products,
                    lsd.dawa_price, lsd.dawa_discount,
                    lsd.amazon_price, lsd.amazon_discount,
                    lsd.nahdi_price, lsd.nahdi_discount,
                    lsd.nahdi_ordered_qty,
                    lsd.noon_sa_price, lsd.noon_sa_discount,
                    lsd.amazon_title, lsd.nahdi_title, lsd.noon_sa_title, lsd.dawa_title,
                    lsd.scraped_date,
                    NULL AS key_name
                FROM client_profile_product p
                LEFT JOIN latest_scraped_data lsd ON p.id = lsd.product_id
                LEFT JOIN client_profile_category c ON p.category_id = c.id
                LEFT JOIN client_profile_subcategory sc ON p.subcategory_id = sc.id
                LEFT JOIN competitor_refs cr ON p.id = cr.product_id
                WHERE lsd.scraped_date IS NOT NULL
                
                UNION ALL

                SELECT
                    NULL AS product_name,
                    NULL AS category_id,
                    NULL AS category_name,
                    NULL AS subcategory_id,
                    NULL AS subcategory_name,
                    NULL AS rsp_vat,
                    NULL AS is_competitor,
                    NULL AS competitor_products,
                    sbd.dawa_price, sbd.dawa_discount,
                    sbd.amazon_price, sbd.amazon_discount,
                    sbd.nahdi_price, sbd.nahdi_discount,
                    sbd.nahdi_ordered_qty,
                    sbd.noon_sa_price, sbd.noon_sa_discount,
                    sbd.amazon_title, sbd.nahdi_title, sbd.noon_sa_title, sbd.dawa_title,
                    sbd.scraped_at::date AS scraped_date,
                    sbd.key_name
                FROM scrapper_scrapedbulkdata sbd
                WHERE sbd.scraped_at >= NOW() - INTERVAL '{days} days'
                AND sbd.key_name IS NOT NULL
            )
            SELECT
                cd.scraped_date,
                COALESCE(cd.product_name, cd.key_name) AS product_name,
                cd.category_name,
                cd.subcategory_name,
                cd.rsp_vat,
                cd.is_competitor,
                cd.competitor_products,
                cd.key_name,
                AVG(cd.dawa_price) AS dawa_price,
                AVG(cd.dawa_discount) AS dawa_discount,
                AVG(cd.amazon_price) AS amazon_price,
                AVG(cd.nahdi_price) AS nahdi_price,
                AVG(cd.noon_sa_price) AS noon_sa_price,
                AVG(cd.amazon_discount) AS amazon_discount,
                AVG(cd.nahdi_discount) AS nahdi_discount,
                AVG(cd.noon_sa_discount) AS noon_sa_discount,
                MAX(cd.nahdi_ordered_qty) AS nahdi_ordered_qty,
                cd.amazon_title,
                cd.nahdi_title,
                cd.noon_sa_title,
                cd.dawa_title,
                NOW() AS refresh_timestamp
            FROM combined_data cd
            GROUP BY 
                cd.scraped_date,
                cd.product_name,
                cd.key_name,
                cd.category_name,
                cd.subcategory_name,
                cd.rsp_vat,
                cd.is_competitor,
                cd.competitor_products,
                cd.amazon_title,
                cd.nahdi_title,
                cd.noon_sa_title,
                cd.dawa_title
            ORDER BY cd.scraped_date DESC;
            """
            
            connection.execute(text(sql))
            logger.info(f"Materialized view '{view_name}' created successfully.")

            connection.execute(text(f"CREATE INDEX idx_{view_name}_product_name ON {view_name} (product_name);"))
            connection.execute(text(f"CREATE INDEX idx_{view_name}_scraped_date ON {view_name} (scraped_date);"))
            connection.execute(text(f"CREATE INDEX idx_{view_name}_is_competitor ON {view_name} (is_competitor) WHERE is_competitor IS NOT NULL;"))
            connection.execute(text(f"CREATE INDEX idx_{view_name}_subcategory_name ON {view_name} (subcategory_name);"))

            setup_refresh_log_table()
            log_refresh(view_name, connection)
    except Exception as e:
        logger.error(f"Error creating materialized view '{view_name}': {e}")
        raise

def refresh_materialized_view(view_name):
    try:
        with engine.begin() as connection:
            # Check if the materialized view exists before refreshing
            result = connection.execute(text(f"""
                SELECT to_regclass('{view_name}');
            """)).scalar()
            
            if result:
                # Ensure the refresh log table exists
                setup_refresh_log_table()
                
                # Refresh the materialized view
                connection.execute(text(f"REFRESH MATERIALIZED VIEW {view_name};"))
                logger.info(f"Materialized view '{view_name}' refreshed successfully.")
                
                # Log the refresh - don't try to update the view directly
                log_refresh(view_name, connection)
            else:
                logger.warning(f"Materialized view '{view_name}' does not exist.")
                # Create it if it doesn't exist
                if view_name == 'last_7_days_view':
                    create_materialized_view('last_7_days_view', 7)
                elif view_name == 'last_30_days_view':
                    create_materialized_view('last_30_days_view', 30)
    except Exception as e:
        logger.error(f"Error refreshing materialized view '{view_name}': {e}")
        raise

def get_last_refresh_time(view_name):
    """Get the last refresh time for a materialized view"""
    try:
        with engine.connect() as connection:
            # First check if our tracking table exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'materialized_view_refresh_log'
                );
            """)).scalar()
            
            if result:
                # Get the last refresh time from our tracking table
                result = connection.execute(text(f"""
                    SELECT refresh_time 
                    FROM materialized_view_refresh_log 
                    WHERE view_name = '{view_name}'
                    ORDER BY refresh_time DESC 
                    LIMIT 1;
                """)).scalar()
                
                if result:
                    return result
            
            # As a fallback, try to get the timestamp from the view itself
            result = connection.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = '{view_name}' AND column_name = 'refresh_timestamp'
                );
            """)).scalar()
            
            if result:
                result = connection.execute(text(f"""
                    SELECT refresh_timestamp 
                    FROM {view_name} 
                    LIMIT 1;
                """)).scalar()
                
                if result:
                    return result
                    
            return "Unknown (no refresh time data available)"
    except Exception as e:
        logger.error(f"Error getting refresh time for {view_name}: {e}")
        return f"Error: {str(e)}"



# For direct execution
if __name__ == "__main__":
    try:
        # Ensure log table exists
        setup_refresh_log_table()
        
        create_materialized_view('last_7_days_view', 7)
        create_materialized_view('last_30_days_view', 30)
        logger.info("All materialized views created successfully.")
        
        # Debug: list all materialized views to confirm they exist
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT schemaname, matviewname FROM pg_matviews;
            """)).fetchall()
            logger.info(f"All materialized views in database: {result}")
            
            # Show refresh times
            last_7_days_refresh = get_last_refresh_time('last_7_days_view')
            last_30_days_refresh = get_last_refresh_time('last_30_days_view')
            logger.info(f"Last refresh time for last_7_days_view: {last_7_days_refresh}")
            logger.info(f"Last refresh time for last_30_days_view: {last_30_days_refresh}")
            
            # Show all refresh logs
            result = connection.execute(text("""
                SELECT view_name, refresh_time 
                FROM materialized_view_refresh_log 
                ORDER BY refresh_time DESC 
                LIMIT 10;
            """)).fetchall()
            logger.info(f"Recent refresh history: {result}")
            
    except Exception as e:
        logger.error(f"Failed to create materialized views: {e}")