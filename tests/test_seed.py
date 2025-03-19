"""
Tests for database seeding functionality.
"""
import pytest
from src.config import get_test_config
from src.query import init_pool, close_pool, query
from src.DAL.seed import seed_database


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Initialize test database for seed tests."""
    config, _ = get_test_config()
    init_pool(config)
    yield
    close_pool()


def clean_database():
    """Clean all tables in the database."""
    query("DELETE FROM likes", commit=True)
    query("DELETE FROM vacations", commit=True)
    query("DELETE FROM users", commit=True)  # Delete all users including admin
    query("DELETE FROM countries", commit=True)


def get_table_counts():
    """Get the count of records in each table."""
    countries_count = query("SELECT COUNT(*) as count FROM countries")[0]['count']
    users_count = query("SELECT COUNT(*) as count FROM users")[0]['count']
    vacations_count = query("SELECT COUNT(*) as count FROM vacations")[0]['count']
    likes_count = query("SELECT COUNT(*) as count FROM likes")[0]['count']
    return countries_count, users_count, vacations_count, likes_count


def test_check_tables_exist_empty():
    """Test check_tables_exist when tables are empty."""
    # First ensure tables are empty
    clean_database()
    
    # Check if tables exist but are empty
    countries_count, users_count, vacations_count, likes_count = get_table_counts()
    
    # Verify all tables are empty
    assert countries_count == 0, "Countries table should be empty"
    assert users_count == 0, "Users table should be empty"
    assert vacations_count == 0, "Vacations table should be empty"
    assert likes_count == 0, "Likes table should be empty"


def test_check_tables_exist_with_data():
    """Test check_tables_exist when tables have data."""
    # Insert some test data
    query("""
        INSERT INTO countries (name, code)
        VALUES ('Test Country', 'TC')
    """, commit=True)
    
    # Check if tables exist and have data
    countries_count, users_count, vacations_count, likes_count = get_table_counts()
    
    # Verify countries table has data but others are empty
    assert countries_count > 0, "Countries table should have data"
    assert users_count == 0, "Users table should be empty"
    assert vacations_count == 0, "Vacations table should be empty"
    assert likes_count == 0, "Likes table should be empty"


def test_seed_database():
    """Test the complete seeding process."""
    # Clean the database completely
    clean_database()
    
    # Run the seeding process
    seed_database()
    
    # Verify data was inserted
    countries_count, users_count, vacations_count, likes_count = get_table_counts()
    
    # Verify all tables have data
    assert countries_count > 0, "Countries table should have data"
    assert users_count > 0, "Users table should have data"
    assert vacations_count > 0, "Vacations table should have data"
    assert likes_count > 0, "Likes table should have data"


def test_seed_database_skip():
    """Test that seeding is skipped when tables already have data."""
    # Clean the database completely first
    clean_database()
    
    # Run the seeding process
    seed_database()
    
    # Get initial counts
    initial_counts = get_table_counts()
    
    # Run seeding again
    seed_database()
    
    # Get final counts
    final_counts = get_table_counts()
    
    # Verify counts haven't changed
    assert initial_counts[0] == final_counts[0], "Countries count should not change"
    assert initial_counts[1] == final_counts[1], "Users count should not change"
    assert initial_counts[2] == final_counts[2], "Vacations count should not change"
    assert initial_counts[3] == final_counts[3], "Likes count should not change" 