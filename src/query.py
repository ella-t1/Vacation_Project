"""
Database query module using psycopg with connection pooling.
"""
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Global connection pool
_pool = None


def init_pool(config, min_size=1, max_size=10):
    """
    Initialize the connection pool.
    
    Args:
        config: Database configuration from config module
        min_size: Minimum number of connections
        max_size: Maximum number of connections
        
    Returns:
        The initialized connection pool
    """
    global _pool
    if _pool is not None:
        close_pool()

    conninfo = (
        f"postgresql://{config.user}:{config.password}@"
        f"{config.host}:{config.port}/{config.database}"
    )
    
    _pool = ConnectionPool(
        conninfo=conninfo,
        min_size=min_size,
        max_size=max_size,
        kwargs={"row_factory": dict_row},
        open=True  # Explicitly set open parameter
    )
    _pool.wait()
    return _pool


@contextmanager
def get_connection():
    """
    Get a database connection from the pool.
    Automatically returns the connection when done.
    """
    if _pool is None:
        raise RuntimeError("Connection pool not initialized. Call init_pool first.")
    
    with _pool.connection() as conn:
        yield conn


@contextmanager
def get_cursor(commit=False):
    """
    Get a database cursor from a pooled connection.
    Automatically handles commit/rollback.
    
    Args:
        commit: Whether to commit the transaction when done
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise


def query(sql, params=None, commit=False):
    """
    Execute a database query and return results.
    
    Args:
        sql: SQL query string
        params: Query parameters (optional)
        commit: Whether to commit the transaction (default: False)
    
    Returns:
        List of dictionaries containing the query results
    
    Example:
        # Select query
        results = query('SELECT * FROM users WHERE id = %s', [user_id])
        
        # Insert/Update/Delete with commit
        query(
            'INSERT INTO users (name, email) VALUES (%s, %s)',
            ['John Doe', 'john@example.com'],
            commit=True
        )
    """
    with get_cursor(commit=commit) as cursor:
        cursor.execute(sql, params)
        if cursor.description:  # If it's a SELECT query
            return cursor.fetchall()
        return None


def close_pool():
    """Close all database connections in the pool."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None 