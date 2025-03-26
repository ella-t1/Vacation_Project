import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from src.models.Vacation import Vacation
from src.models.Country import Country
from src.dal.VacationService import VacationService
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
def cleanup_data():
    """Clean up test data after each test."""
    yield
    query("DELETE FROM likes", commit=True)
    query("DELETE FROM vacations", commit=True)
    query("DELETE FROM countries WHERE code != 'US'", commit=True)  # Keep default country

@pytest.fixture
def test_country():
    """Create a test country."""
    country = CountryService.create(Country(
        name="Test Country",
        code="TC"
    ))
    return country

@pytest.fixture
def future_dates():
    """Get future start and end dates for testing."""
    today = date.today()
    return {
        'start': today + timedelta(days=1),
        'end': today + timedelta(days=8)
    }

# Model Tests
def test_vacation_creation(test_country, future_dates):
    """Test creating a Vacation instance."""
    vacation = Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    )
    
    assert vacation.country_id == test_country.id
    assert vacation.destination == "Test Resort"
    assert vacation.description == "A lovely resort"
    assert vacation.start_date == future_dates['start']
    assert vacation.end_date == future_dates['end']
    assert vacation.price == Decimal("999.99")
    assert isinstance(vacation.created_at, datetime)

def test_vacation_validation(test_country, future_dates):
    """Test vacation validation."""
    # Test invalid destination
    with pytest.raises(ValueError, match="Destination must be a non-empty string"):
        Vacation(
            country_id=test_country.id,
            destination="",
            description="Test",
            start_date=future_dates['start'],
            end_date=future_dates['end'],
            price=Decimal("100")
        )
    
    # Test invalid dates
    with pytest.raises(ValueError, match="End date must be after start date"):
        Vacation(
            country_id=test_country.id,
            destination="Test Resort",
            description="Test",
            start_date=future_dates['end'],
            end_date=future_dates['start'],
            price=Decimal("100")
        )
    
    # Test past date
    past_date = date.today() - timedelta(days=1)
    with pytest.raises(ValueError, match="Start date cannot be in the past"):
        Vacation(
            country_id=test_country.id,
            destination="Test Resort",
            description="Test",
            start_date=past_date,
            end_date=future_dates['end'],
            price=Decimal("100")
        )
    
    # Test invalid price
    with pytest.raises(ValueError, match="Price must be greater than zero"):
        Vacation(
            country_id=test_country.id,
            destination="Test Resort",
            description="Test",
            start_date=future_dates['start'],
            end_date=future_dates['end'],
            price=Decimal("0")
        )

def test_vacation_to_dict(test_country, future_dates):
    """Test converting Vacation to dictionary."""
    vacation = Vacation(
        id=1,
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99"),
        country=test_country
    )
    
    data = vacation.to_dict()
    assert data['id'] == 1
    assert data['country_id'] == test_country.id
    assert data['destination'] == "Test Resort"
    assert data['description'] == "A lovely resort"
    assert data['start_date'] == future_dates['start'].isoformat()
    assert data['end_date'] == future_dates['end'].isoformat()
    assert data['price'] == "999.99"
    assert data['country'] == test_country.to_dict()

def test_vacation_from_dict(test_country, future_dates):
    """Test creating Vacation from dictionary."""
    data = {
        'id': 1,
        'country_id': test_country.id,
        'destination': "Test Resort",
        'description': "A lovely resort",
        'start_date': future_dates['start'].isoformat(),
        'end_date': future_dates['end'].isoformat(),
        'price': "999.99",
        'country': test_country.to_dict()
    }
    
    vacation = Vacation.from_dict(data)
    assert vacation.id == 1
    assert vacation.country_id == test_country.id
    assert vacation.destination == "Test Resort"
    assert vacation.description == "A lovely resort"
    assert vacation.start_date == future_dates['start']
    assert vacation.end_date == future_dates['end']
    assert vacation.price == Decimal("999.99")
    assert vacation.country.id == test_country.id

# Service Tests
def test_create_vacation(test_country, future_dates):
    """Test creating a vacation in the database."""
    vacation = Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    )
    
    saved = VacationService.create(vacation)
    assert saved.id is not None
    assert saved.destination == "Test Resort"
    assert saved.country.id == test_country.id

def test_create_vacation_invalid_country(future_dates):
    """Test creating a vacation with non-existent country."""
    vacation = Vacation(
        country_id=999,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    )
    
    with pytest.raises(ValueError, match="Country with id 999 not found"):
        VacationService.create(vacation)

def test_get_vacation_by_id(test_country, future_dates):
    """Test retrieving a vacation by ID."""
    vacation = VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    ))
    
    retrieved = VacationService.get_by_id(vacation.id)
    assert retrieved is not None
    assert retrieved.id == vacation.id
    assert retrieved.destination == vacation.destination
    assert retrieved.country.id == test_country.id

def test_update_vacation(test_country, future_dates):
    """Test updating a vacation."""
    vacation = VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    ))
    
    vacation.destination = "Updated Resort"
    vacation.price = Decimal("1099.99")
    updated = VacationService.update(vacation)
    
    assert updated.destination == "Updated Resort"
    assert updated.price == Decimal("1099.99")

def test_update_nonexistent_vacation(test_country, future_dates):
    """Test updating a non-existent vacation."""
    vacation = Vacation(
        id=999,
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    )
    
    with pytest.raises(ValueError, match="Vacation with id 999 not found"):
        VacationService.update(vacation)

def test_delete_vacation(test_country, future_dates):
    """Test deleting a vacation."""
    vacation = VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    ))
    
    assert VacationService.delete(vacation.id) is True
    assert VacationService.get_by_id(vacation.id) is None

def test_delete_vacation_with_likes(test_country, future_dates):
    """Test deleting a vacation that has associated likes."""
    vacation = VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Test Resort",
        description="A lovely resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    ))
    
    # Create a like for this vacation
    query("""
        INSERT INTO likes (user_id, vacation_id)
        VALUES (%s, %s)
    """, [1, vacation.id], commit=True)
    
    with pytest.raises(ValueError, match="Cannot delete vacation with associated likes"):
        VacationService.delete(vacation.id)

def test_get_all_vacations(test_country, future_dates):
    """Test retrieving all vacations with filtering."""
    # Create test vacations
    vacations = [
        Vacation(
            country_id=test_country.id,
            destination=f"Resort {i}",
            description=f"Description {i}",
            start_date=future_dates['start'] + timedelta(days=i),
            end_date=future_dates['end'] + timedelta(days=i),
            price=Decimal(f"{1000 + i}.99")
        )
        for i in range(3)
    ]
    
    for vacation in vacations:
        VacationService.create(vacation)
    
    # Test basic retrieval
    all_vacations = VacationService.get_all()
    assert len(all_vacations) >= 3
    
    # Test price filtering
    filtered = VacationService.get_all(min_price=Decimal("1001"), max_price=Decimal("1002"))
    assert len(filtered) == 1
    assert filtered[0].price == Decimal("1001.99")
    
    # Test date filtering
    date_filtered = VacationService.get_all(
        start_date=future_dates['start'] + timedelta(days=1)
    )
    assert len(date_filtered) == 2
    
    # Test sorting
    sorted_desc = VacationService.get_all(sort_by='price', sort_order='desc')
    prices = [v.price for v in sorted_desc]
    assert prices == sorted(prices, reverse=True)

def test_search_vacations(test_country, future_dates):
    """Test searching vacations."""
    # Create test vacations
    VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Beach Resort",
        description="A lovely beach resort",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("999.99")
    ))
    
    VacationService.create(Vacation(
        country_id=test_country.id,
        destination="Mountain Lodge",
        description="A cozy mountain retreat",
        start_date=future_dates['start'],
        end_date=future_dates['end'],
        price=Decimal("899.99")
    ))
    
    # Search by destination
    results = VacationService.search("Beach")
    assert len(results) == 1
    assert "Beach" in results[0].destination
    
    # Search by description
    results = VacationService.search("mountain")
    assert len(results) == 1
    assert "mountain" in results[0].description.lower()
    
    # No results
    results = VacationService.search("desert")
    assert len(results) == 0

def test_count_vacations(test_country, future_dates):
    """Test counting vacations."""
    initial_count = VacationService.count()
    
    # Create test vacations
    for i in range(3):
        VacationService.create(Vacation(
            country_id=test_country.id,
            destination=f"Resort {i}",
            description=f"Description {i}",
            start_date=future_dates['start'],
            end_date=future_dates['end'],
            price=Decimal("999.99")
        ))
    
    # Test total count
    assert VacationService.count() == initial_count + 3
    
    # Test count by country
    assert VacationService.count(country_id=test_country.id) == 3 