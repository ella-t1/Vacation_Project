"""
Tests for the query module using real database connections.
"""
import pytest
from src.config import get_test_config
from src.query import init_pool, query, close_pool, get_cursor, get_connection


@pytest.fixture(scope="module")
def db_config():
    """Get test database configuration."""
    config, _ = get_test_config()
    return config


@pytest.fixture(scope="module")
def pool(db_config):
    """Initialize and clean up the connection pool."""
    init_pool(db_config)
    yield
    close_pool()


def test_simple_select(pool):
    """Test simple SELECT query."""
    result = query('SELECT 1 + 1 as sum')
    assert len(result) == 1
    assert result[0]['sum'] == 2


def test_parameterized_query(pool):
    """Test query with parameters."""
    a, b = 5, 3
    result = query('SELECT %s + %s as sum', [a, b])
    assert result[0]['sum'] == 8


def test_multiple_rows(pool):
    """Test query returning multiple rows."""
    result = query('''
        SELECT 
            generate_series(1, 3) as num,
            generate_series(1, 3) * 2 as double
    ''')
    assert len(result) == 3
    assert result[0]['num'] == 1
    assert result[0]['double'] == 2
    assert result[2]['num'] == 3
    assert result[2]['double'] == 6


def test_no_results(pool):
    """Test query with no results."""
    result = query('SELECT 1 WHERE 1=2')
    assert result == []


def test_insert_and_select(pool):
    """Test insert with commit and select."""
    # Create a temporary table
    query('''
        CREATE TEMP TABLE test_table (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
    ''', commit=True)
    
    # Insert data
    query(
        'INSERT INTO test_table (name) VALUES (%s)',
        ['test_name'],
        commit=True
    )
    
    # Select data
    result = query('SELECT * FROM test_table')
    assert len(result) == 1
    assert result[0]['name'] == 'test_name'


def test_transaction_rollback(pool):
    """Test transaction rollback on error."""
    # Create a temporary table
    query('''
        CREATE TEMP TABLE test_rollback (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''', commit=True)
    
    # This should fail and rollback
    with pytest.raises(Exception):
        query(
            'INSERT INTO test_rollback (name) VALUES (%s)',
            [None],  # This will violate NOT NULL constraint
            commit=True
        )
    
    # Verify no data was inserted
    result = query('SELECT COUNT(*) as count FROM test_rollback')
    assert result[0]['count'] == 0


def test_cursor_context_manager(pool):
    """Test the cursor context manager."""
    with get_cursor() as cursor:
        cursor.execute('SELECT 42 as answer')
        result = cursor.fetchall()
        assert result[0]['answer'] == 42


def test_connection_context_manager(pool):
    """Test the connection context manager."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 42 as answer')
            result = cursor.fetchone()
            assert result['answer'] == 42


def test_concurrent_queries(pool):
    """Test running multiple queries in sequence."""
    results = []
    for i in range(5):
        result = query('SELECT %s as num', [i])
        results.append(result[0]['num'])
    
    assert results == [0, 1, 2, 3, 4]


def test_special_characters(pool):
    """Test handling of special characters in parameters."""
    special_text = "Test's string with \"quotes\" and % signs"
    result = query(
        'SELECT %s as special_text',
        [special_text]
    )
    assert result[0]['special_text'] == special_text 