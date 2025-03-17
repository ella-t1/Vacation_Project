import pytest
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.create_db import (
    get_postgres_params,
    create_database,
    init_schema,
    validate_tables,
    setup_database
)
from src.config import DB_CONFIG

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables before all tests."""
    # Environment variables are already loaded from .env.test in conftest.py
    pass

@pytest.fixture
def postgres_params():
    """Get postgres connection parameters."""
    return get_postgres_params()

@pytest.fixture
def test_db_config():
    """Get test database configuration."""
    return DB_CONFIG

class TestDatabaseSetup:
    def test_get_postgres_params(self, postgres_params):
        """Test getting postgres connection parameters."""
        assert postgres_params['dbname'] == 'postgres'
        assert postgres_params['user'] == os.getenv('POSTGRES_USER')
        assert postgres_params['host'] == os.getenv('POSTGRES_HOST')
        assert postgres_params['password'] == os.getenv('POSTGRES_PASSWORD')

    def test_create_database(self, postgres_params):
        """Test database creation."""
        # Test creating database
        create_database()
        
        # Verify database exists
        conn = psycopg2.connect(**postgres_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv('POSTGRES_DATABASE'),))
        exists = cur.fetchone()
        
        assert exists is not None
        assert exists[0] == 1
        
        cur.close()
        conn.close()

    def test_init_schema(self, test_db_config):
        """Test schema initialization."""
        # First create the database
        create_database()
        
        # Initialize schema
        init_schema()
        
        # Verify tables were created
        conn = psycopg2.connect(**test_db_config)
        cur = conn.cursor()
        
        # Check if all required tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = {row[0] for row in cur.fetchall()}
        
        required_tables = {'countries', 'users', 'vacations', 'likes'}
        assert all(table in tables for table in required_tables)
        
        cur.close()
        conn.close()

    def test_validate_tables(self, test_db_config):
        """Test table validation."""
        # First create the database and ensure tables exist
        create_database()
        init_schema()
        
        # Validate tables
        validate_tables()  # Should not raise any exceptions
        
        # Test with missing table
        conn = psycopg2.connect(**test_db_config)
        cur = conn.cursor()
        
        # Drop a table to test validation
        cur.execute("DROP TABLE IF EXISTS likes")
        conn.commit()
        
        with pytest.raises(ValueError, match="Required table 'likes' was not created"):
            validate_tables()
        
        cur.close()
        conn.close()

    def test_setup_database(self, test_db_config):
        """Test complete database setup process."""
        # Run complete setup
        setup_database()
        
        # Verify database and tables exist
        conn = psycopg2.connect(**test_db_config)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv('POSTGRES_DATABASE'),))
        assert cur.fetchone() is not None
        
        # Check if all required tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = {row[0] for row in cur.fetchall()}
        
        required_tables = {'countries', 'users', 'vacations', 'likes'}
        assert all(table in tables for table in required_tables)
        
        cur.close()
        conn.close()

    def test_table_structures(self, test_db_config):
        """Test that tables have correct column structures."""
        # First create the database and ensure tables exist
        create_database()
        init_schema()
        
        conn = psycopg2.connect(**test_db_config)
        cur = conn.cursor()
        
        # Define expected column structures
        expected_columns = {
            'countries': ['id', 'name', 'code', 'created_at'],
            'users': ['id', 'first_name', 'last_name', 'email', 'password', 'role_id', 'created_at'],
            'vacations': ['id', 'country_id', 'destination', 'description', 'start_date', 'end_date', 'price', 'image_url', 'created_at'],
            'likes': ['id', 'user_id', 'vacation_id', 'created_at']
        }
        
        # Check each table's structure
        for table, expected_cols in expected_columns.items():
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """)
            actual_cols = [row[0] for row in cur.fetchall()]
            assert set(actual_cols) == set(expected_cols), f"Table {table} has incorrect structure"
        
        cur.close()
        conn.close()

    @pytest.fixture(autouse=True)
    def cleanup(self, postgres_params):
        """Clean up after each test."""
        yield
        
        # Connect to postgres database to drop test database
        conn = psycopg2.connect(**postgres_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Drop test database if it exists
        cur.execute(f"DROP DATABASE IF EXISTS {os.getenv('POSTGRES_DATABASE')}")
        
        cur.close()
        conn.close() 