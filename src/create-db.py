import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_CONFIG, DatabaseConnection

def get_postgres_params():
    """Get connection parameters for postgres database (for initial connection)."""
    params = DB_CONFIG.copy()
    params['dbname'] = 'postgres'  # Connect to default postgres database
    return params

def create_database():
    """Create the database if it doesn't exist."""
    postgres_params = get_postgres_params()
    
    try:
        # Connect to postgres database
        conn = psycopg2.connect(**postgres_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {DB_CONFIG['dbname']}...")
            cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
            print(f"Database {DB_CONFIG['dbname']} created successfully!")
        else:
            print(f"Database {DB_CONFIG['dbname']} already exists.")
            
    except Exception as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def init_schema():
    """Initialize the database schema."""
    try:
        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        print("Initializing database schema...")
        
        # Use DatabaseConnection context manager
        with DatabaseConnection() as cur:
            cur.execute(schema_sql)
            
        print("Schema initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing schema: {e}")
        raise

def validate_tables():
    """Validate that all required tables exist and have the correct structure."""
    required_tables = {
        'countries': ['id', 'name', 'code', 'created_at'],
        'users': ['id', 'first_name', 'last_name', 'email', 'password', 'role_id', 'created_at'],
        'vacations': ['id', 'country_id', 'destination', 'description', 'start_date', 'end_date', 'price', 'image_url', 'created_at'],
        'likes': ['id', 'user_id', 'vacation_id', 'created_at']
    }
    
    try:
        with DatabaseConnection() as cur:
            # Check if tables exist
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            existing_tables = {row[0] for row in cur.fetchall()}
            
            # Check each required table
            for table, columns in required_tables.items():
                if table not in existing_tables:
                    raise ValueError(f"Required table '{table}' was not created")
                
                # Check table structure
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                """)
                existing_columns = {row[0] for row in cur.fetchall()}
                
                missing_columns = set(columns) - existing_columns
                if missing_columns:
                    raise ValueError(f"Table '{table}' is missing columns: {', '.join(missing_columns)}")
                
                print(f"✓ Table '{table}' validated successfully")
            
            print("All tables validated successfully!")
            
    except Exception as e:
        print(f"Error validating tables: {e}")
        raise

def setup_database():
    """Set up the database and initialize schema."""
    try:
        create_database()
        init_schema()
        validate_tables()
        print("Database setup completed successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    print("Starting database setup process...")
    setup_database() 