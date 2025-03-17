import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DATABASE', 'vacation_db'),
    'user': os.getenv('POSTGRES_USER', 'db_admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'pg_admin123'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

class DatabaseConnection:
    """Context manager for database connections"""
    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
            return self.cur
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()

