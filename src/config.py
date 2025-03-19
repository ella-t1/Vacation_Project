"""
Configuration module for database and application settings.
Handles loading of environment variables for different environments.
"""
import os
from collections import namedtuple
from dotenv import load_dotenv


# Simple named tuple for database configuration
DBConfig = namedtuple('DBConfig', ['user', 'password', 'host', 'port', 'database'])


def get_config():
    """
    Get application configuration.
    
    Returns:
        Dictionary containing application configuration
    """
    # Load environment variables
    load_dotenv()
    
    return {
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
        'JWT_EXPIRY_HOURS': os.getenv('JWT_EXPIRY_HOURS', '24'),
        'POSTGRES_USER': os.getenv('POSTGRES_USER', 'db_admin'),
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', 'pg_admin123'),
        'POSTGRES_HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'POSTGRES_PORT': os.getenv('POSTGRES_PORT', '5433'),
        'POSTGRES_DATABASE': os.getenv('POSTGRES_DATABASE', 'vacation_db_staging')
    }


def get_connection_string(config):
    """
    Generate a PostgreSQL connection string.
    
    Args:
        config: Database configuration
        
    Returns:
        PostgreSQL connection URL
    """
    return f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"


def load_db_config(env_file=None):
    """
    Load database configuration from environment file.
    
    Args:
        env_file: Path to environment file. If None, uses default environment variables
        
    Returns:
        Database configuration
    """
    # Load environment variables from file if specified
    if env_file:
        # Override existing variables
        load_dotenv(env_file, override=True)
    
    return DBConfig(
        user=os.getenv('POSTGRES_USER', 'db_admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'pg_admin123'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5433')),
        database=os.getenv('POSTGRES_DATABASE', 'vacation_db_staging')
    )


def get_staging_config():
    """
    Get staging database configuration and connection string.
    
    Returns:
        Tuple of (database config, connection string)
    """
    config = load_db_config('.env')
    return config, get_connection_string(config)


def get_test_config():
    """
    Get test database configuration and connection string.
    
    Returns:
        Tuple of (database config, connection string)
    """
    config = load_db_config('.env.test')
    return config, get_connection_string(config)


# Example usage:
if __name__ == '__main__':
    # Get configurations
    staging_config, staging_url = get_staging_config()
    test_config, test_url = get_test_config()
    
    # Print configurations for verification
    print("Staging Database URL:", staging_url)
    print("Test Database URL:", test_url) 