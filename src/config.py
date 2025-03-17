import os
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DATABASE'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
}

# Add SSL mode only if using Neon database
if 'neon' in os.getenv('POSTGRES_HOST', ''):
    DB_CONFIG['sslmode'] = 'require'

@contextmanager
def DatabaseConnection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        # Create cursor with RealDictCursor to return results as dictionaries
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            if 'cur' in locals():
                cur.close()
            conn.close()

