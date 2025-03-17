import pytest
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

def get_postgres_params():
    """Get connection parameters for postgres database."""
    return {
        'dbname': 'postgres',
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }

def create_test_database():
    """Create test database if it doesn't exist."""
    postgres_params = get_postgres_params()
    test_db_name = os.getenv('POSTGRES_DATABASE')
    
    try:
        # Connect to postgres database
        conn = psycopg2.connect(**postgres_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating test database {test_db_name}...")
            cur.execute(f"CREATE DATABASE {test_db_name}")
            print(f"Test database {test_db_name} created successfully!")
        else:
            print(f"Test database {test_db_name} already exists.")
            
    except Exception as e:
        print(f"Error creating test database: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def pytest_configure(config):
    """Load test environment variables before any tests run."""
    # Load test environment variables from .env.test
    load_dotenv('.env.test', override=True)  # Add override=True to ensure test env vars take precedence
    
    # Verify test environment variables are set
    required_vars = [
        'POSTGRES_USER',
        'POSTGRES_HOST',
        'POSTGRES_PASSWORD',
        'POSTGRES_DATABASE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create test database
    create_test_database()

@pytest.fixture(scope="session")
def test_db_name():
    """Get the test database name."""
    return os.getenv('POSTGRES_DATABASE', 'vacation_db_test') 