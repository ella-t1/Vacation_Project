import pytest
from datetime import datetime, UTC
from src.models.Country import Country
from src.dal.CountryService import CountryService
from src.config import get_test_config
from src.query import init_pool, close_pool, query

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Initialize database connection for tests."""
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
    with open('SQL/schema.sql', 'r') as f:
        schema_sql = f.read()
        query(schema_sql, commit=True)
    
    yield
    close_pool()

@pytest.fixture(autouse=True)
def cleanup_countries():
    """Clean up countries table after each test."""
    yield
    # Clean up vacations first due to foreign key constraints
    query("DELETE FROM vacations", commit=True)
    query("DELETE FROM countries", commit=True)

# Model Tests
def test_country_creation():
    """Test creating a Country instance."""
    country = Country(name="United States", code="US")
    assert country.name == "United States"
    assert country.code == "US"
    assert isinstance(country.created_at, datetime)

def test_country_code_validation():
    """Test country code validation."""
    # Test valid codes
    assert Country._validate_code("US") == "US"
    assert Country._validate_code("us") == "US"
    assert Country._validate_code(" gb ") == "GB"
    
    # Test invalid codes
    with pytest.raises(ValueError, match="Country code must be a string"):
        Country._validate_code(None)
    
    with pytest.raises(ValueError, match="Country code must be exactly 2 characters"):
        Country._validate_code("USA")

def test_country_to_dict():
    """Test converting Country to dictionary."""
    now = datetime.now(UTC)
    country = Country(
        id=1,
        name="United States",
        code="US",
        created_at=now
    )
    data = country.to_dict()
    
    assert data['id'] == 1
    assert data['name'] == "United States"
    assert data['code'] == "US"
    assert data['created_at'] == now.isoformat()

def test_country_from_dict():
    """Test creating Country from dictionary."""
    now = datetime.now(UTC)
    data = {
        'id': 1,
        'name': "United States",
        'code': "US",
        'created_at': now.isoformat()
    }
    country = Country.from_dict(data)
    
    assert country.id == 1
    assert country.name == "United States"
    assert country.code == "US"
    assert country.created_at == now

# Service Tests
def test_create_country():
    """Test creating a country in the database."""
    country = Country(name="Canada", code="CA")
    saved = CountryService.create(country)
    
    assert saved.id is not None
    assert saved.name == "Canada"
    assert saved.code == "CA"
    assert isinstance(saved.created_at, datetime)

def test_create_duplicate_code():
    """Test creating a country with duplicate code."""
    CountryService.create(Country(name="Canada", code="CA"))
    
    with pytest.raises(ValueError, match="Country with code CA already exists"):
        CountryService.create(Country(name="Canada 2", code="CA"))

def test_get_by_id():
    """Test retrieving a country by ID."""
    created = CountryService.create(Country(name="Mexico", code="MX"))
    retrieved = CountryService.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name
    assert retrieved.code == created.code

def test_get_by_code():
    """Test retrieving a country by code."""
    created = CountryService.create(Country(name="Brazil", code="BR"))
    
    # Test with different case
    retrieved = CountryService.get_by_code("br")
    assert retrieved is not None
    assert retrieved.id == created.id
    
    # Test non-existent code
    assert CountryService.get_by_code("XX") is None

def test_update_country():
    """Test updating a country."""
    country = CountryService.create(Country(name="Argentina", code="AR"))
    
    country.name = "Argentine Republic"
    country.code = "AG"
    updated = CountryService.update(country)
    
    assert updated.name == "Argentine Republic"
    assert updated.code == "AG"

def test_update_nonexistent_country():
    """Test updating a non-existent country."""
    country = Country(id=999, name="Test", code="XX")
    with pytest.raises(ValueError, match="Country with id 999 not found"):
        CountryService.update(country)

def test_update_duplicate_code():
    """Test updating a country with a code that's already in use."""
    CountryService.create(Country(name="Chile", code="CL"))
    country2 = CountryService.create(Country(name="Peru", code="PE"))
    
    country2.code = "CL"
    with pytest.raises(ValueError, match="Country code CL is already in use"):
        CountryService.update(country2)

def test_delete_country():
    """Test deleting a country."""
    country = CountryService.create(Country(name="Colombia", code="CO"))
    assert CountryService.delete(country.id) is True
    assert CountryService.get_by_id(country.id) is None

def test_delete_country_with_vacations():
    """Test deleting a country that has associated vacations."""
    country = CountryService.create(Country(name="Ecuador", code="EC"))
    
    # Create a vacation for this country
    query("""
        INSERT INTO vacations (
            country_id, destination, description,
            start_date, end_date, price
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """, [
        country.id,
        "Test Destination",
        "Test Description",
        "2024-01-01",
        "2024-01-07",
        999.99
    ], commit=True)
    
    with pytest.raises(ValueError, match="Cannot delete country with associated vacations"):
        CountryService.delete(country.id)

def test_get_all_countries():
    """Test retrieving all countries."""
    # Create some test countries
    countries = [
        Country(name="France", code="FR"),
        Country(name="Germany", code="DE"),
        Country(name="Italy", code="IT")
    ]
    for country in countries:
        CountryService.create(country)
    
    # Retrieve all countries
    all_countries = CountryService.get_all()
    assert len(all_countries) >= 3
    
    # Verify they're sorted by name
    names = [c.name for c in all_countries]
    assert names == sorted(names)

def test_search_countries():
    """Test searching countries."""
    # Create test countries
    CountryService.create(Country(name="Spain", code="ES"))
    CountryService.create(Country(name="Portugal", code="PT"))
    CountryService.create(Country(name="Greece", code="GR"))
    
    # Search by name
    results = CountryService.search("Port")
    assert len(results) == 1
    assert "Port" in results[0].name
    
    # Search by code
    results = CountryService.search("ES")
    assert len(results) == 1
    assert results[0].code == "ES"
    
    # Case-insensitive search
    results = CountryService.search("spain")
    assert len(results) >= 1
    
    # No results
    results = CountryService.search("XYZ")
    assert len(results) == 0

def test_count_countries():
    """Test counting countries."""
    initial_count = CountryService.count()
    
    # Add some test countries
    CountryService.create(Country(name="Netherlands", code="NL"))
    CountryService.create(Country(name="Belgium", code="BE"))
    
    assert CountryService.count() == initial_count + 2 