"""
Tests for the configuration module.
"""
import os
import pytest
from src.config import (
    DBConfig,
    get_connection_string,
    load_db_config,
    get_staging_config,
    get_test_config
)


@pytest.fixture
def mock_env_vars():
    """Fixture to set and cleanup environment variables."""
    # Save original environment variables
    original_vars = {
        'POSTGRES_USER': os.environ.get('POSTGRES_USER'),
        'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
        'POSTGRES_PORT': os.environ.get('POSTGRES_PORT'),
        'POSTGRES_DATABASE': os.environ.get('POSTGRES_DATABASE')
    }
    
    # Set test environment variables
    os.environ['POSTGRES_USER'] = 'test_user'
    os.environ['POSTGRES_PASSWORD'] = 'test_pass'
    os.environ['POSTGRES_HOST'] = 'test_host'
    os.environ['POSTGRES_PORT'] = '5433'
    os.environ['POSTGRES_DATABASE'] = 'test_db'
    
    yield
    
    # Restore original environment variables
    for key, value in original_vars.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_dbconfig_creation():
    """Test creating a DBConfig instance."""
    config = DBConfig('user', 'pass', 'host', 5432, 'db')
    
    assert config.user == 'user'
    assert config.password == 'pass'
    assert config.host == 'host'
    assert config.port == 5432
    assert config.database == 'db'


def test_get_connection_string():
    """Test connection string generation."""
    config = DBConfig('user', 'pass', 'host', 5432, 'db')
    url = get_connection_string(config)
    
    assert url == 'postgresql://user:pass@host:5432/db'


def test_load_db_config_with_env_vars(mock_env_vars):
    """Test loading config from environment variables."""
    config = load_db_config()
    
    assert config.user == 'test_user'
    assert config.password == 'test_pass'
    assert config.host == 'test_host'
    assert config.port == 5433
    assert config.database == 'test_db'


def test_load_db_config_defaults():
    """Test loading config with default values."""
    # Clear any existing environment variables that might affect defaults
    for var in ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE']:
        if var in os.environ:
            del os.environ[var]
            
    config = load_db_config()
    
    assert config.user == 'db_admin'
    assert config.password == 'pg_admin123'
    assert config.host == 'localhost'
    assert config.port == 5433
    assert config.database == os.getenv('POSTGRES_DATABASE', 'vacations')


def test_get_staging_config():
    """Test getting staging configuration."""
    config, url = get_staging_config()
    
    assert isinstance(config, DBConfig)
    assert isinstance(url, str)
    assert 'postgresql://' in url
    assert config.database == os.getenv('POSTGRES_DATABASE', 'vacations')


def test_get_test_config():
    """Test getting test configuration."""
    config, url = get_test_config()
    
    assert isinstance(config, DBConfig)
    assert isinstance(url, str)
    assert 'postgresql://' in url
    assert config.database == os.getenv('POSTGRES_DATABASE', 'vacations')
    assert str(config.port) == '5432' 