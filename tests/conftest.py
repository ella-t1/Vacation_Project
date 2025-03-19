"""
Test configuration and fixtures.
"""
import pytest
from src.config import get_test_config
from src.query import init_pool, close_pool, query


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialize test database for all tests."""
    print("\nInitializing test database...")  # Debug print
    config, _ = get_test_config()
    init_pool(config)
    
    # Drop existing schema
    cleanup_sql = """
        DROP TYPE IF EXISTS role_enum CASCADE;
        DROP TABLE IF EXISTS likes CASCADE;
        DROP TABLE IF EXISTS vacations CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS countries CASCADE;
    """
    query(cleanup_sql, commit=True)
    
    # Initialize schema
    print("Creating schema...")  # Debug print
    with open('SQL/schema.sql', 'r') as f:
        schema_sql = f.read()
        query(schema_sql, commit=True)
    print("Schema created successfully")  # Debug print
    
    yield
    
    print("Cleaning up test database...")  # Debug print
    close_pool()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Clean up all tables except admin user in correct order
    query("DELETE FROM likes", commit=True)  # Delete likes first
    query("DELETE FROM vacations", commit=True)  # Then vacations
    query("DELETE FROM users WHERE email != 'admin@example.com'", commit=True)  # Then users
    query("DELETE FROM countries", commit=True)  # Finally countries 