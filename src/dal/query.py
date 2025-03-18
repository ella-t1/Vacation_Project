import bcrypt
from typing import Optional, List, Dict, Any, Tuple
from config import DatabaseConnection

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def query(sql: str, params: Optional[Tuple[Any, ...]] = None, fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a SQL query with optional parameters and return results if fetch is True.
    
    Args:
        sql: The SQL query to execute
        params: Optional tuple of parameters for the query
        fetch: Whether to fetch and return results (True for SELECT, False for INSERT/UPDATE/DELETE)
    
    Returns:
        List of dictionaries containing query results if fetch is True, None otherwise
    
    Raises:
        Exception: If there is an error executing the query
    
    Example:
        # SELECT query with parameters
        results = query("SELECT * FROM users WHERE email = %s", ('user@example.com',))
        
        # INSERT query
        query("INSERT INTO users (name, email) VALUES (%s, %s)", ('John', 'john@example.com'), fetch=False)
    """
    with DatabaseConnection() as cur:
        try:
            cur.execute(sql, params)
            if fetch:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            raise