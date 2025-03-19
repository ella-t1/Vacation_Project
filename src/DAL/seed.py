"""
Database seeding module that executes schema.sql only if tables don't exist or are empty.
"""
from src.query import query


def check_tables_exist():
    """Check if all required tables exist and have data."""
    print("Checking existing tables...")
    
    # Check if tables exist
    tables = query("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    found_tables = {table['table_name'] for table in tables}
    expected_tables = {'countries', 'users', 'vacations', 'likes'}
    
    if not expected_tables.issubset(found_tables):
        missing_tables = expected_tables - found_tables
        print(f"Missing tables: {', '.join(missing_tables)}")
        return False
    
    # Check if tables have data
    for table in expected_tables:
        count = query(f"SELECT COUNT(*) as count FROM {table}")[0]['count']
        if count == 0:
            print(f"Table {table} exists but is empty")
            return False
    
    print("All tables exist and contain data")
    return True


def seed_database():
    """Execute schema.sql to create and populate the database."""
    print("Starting database check...")
    
    # Check if tables exist and have data
    if check_tables_exist():
        print("Database is already seeded. Skipping...")
        return
    
    # If we get here, we need to create/seed the tables
    print("Executing schema.sql...")
    with open('SQL/schema.sql', 'r') as f:
        schema_sql = f.read()
        query(schema_sql, commit=True)
    
    # Verify the seeding worked
    if check_tables_exist():
        print("Database seeded successfully!")
    else:
        print("Warning: Database seeding may have failed. Please check the tables.")


if __name__ == "__main__":
    seed_database()