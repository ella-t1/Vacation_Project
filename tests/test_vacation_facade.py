"""
Tests for the VacationFacade class.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from src.facades.VacationFacade import VacationFacade
from src.dal.UserService import UserService
from src.models.User import User
from src.query import query


@pytest.fixture(autouse=True)
def setup_countries():
    """Insert sample countries before each test."""
    # Insert sample countries
    query("""
        INSERT INTO countries (name, code) VALUES
        ('United States', 'US'),
        ('United Kingdom', 'GB'),
        ('France', 'FR'),
        ('Italy', 'IT'),
        ('Spain', 'ES')
        ON CONFLICT (code) DO NOTHING;
    """, commit=True)
    
    yield
    # Cleanup is handled by conftest.py cleanup_test_data fixture


@pytest.fixture
def vacation_facade():
    """Create VacationFacade instance."""
    return VacationFacade()


@pytest.fixture
def test_user():
    """Create a test user."""
    user = User(
        first_name="Test",
        last_name="User",
        email="test.user@example.com",
        password="password123"
    )
    return UserService.create(user)


@pytest.fixture
def test_vacation(vacation_facade):
    """Create a test vacation."""
    return vacation_facade.create_vacation(
        country_code="US",
        destination="Test Destination",
        description="Test Description",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=20),
        price=Decimal("1000.00"),
        image_url="http://example.com/image.jpg"
    )


def test_create_vacation(vacation_facade):
    """Test creating a vacation."""
    start_date = date.today() + timedelta(days=10)
    end_date = date.today() + timedelta(days=20)
    
    vacation = vacation_facade.create_vacation(
        country_code="US",
        destination="New York City",
        description="Experience the Big Apple",
        start_date=start_date,
        end_date=end_date,
        price=Decimal("1500.00"),
        image_url="http://example.com/nyc.jpg"
    )
    
    assert vacation['destination'] == "New York City"
    assert vacation['description'] == "Experience the Big Apple"
    assert vacation['start_date'] == start_date
    assert vacation['end_date'] == end_date
    assert vacation['price'] == Decimal("1500.00")
    assert vacation['image_url'] == "http://example.com/nyc.jpg"


def test_create_vacation_invalid_country(vacation_facade):
    """Test creating a vacation with invalid country code."""
    with pytest.raises(ValueError, match="Invalid country code: XX"):
        vacation_facade.create_vacation(
            country_code="XX",
            destination="Invalid",
            description="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            price=Decimal("100.00")
        )


def test_create_vacation_invalid_dates(vacation_facade):
    """Test creating a vacation with invalid dates."""
    with pytest.raises(ValueError, match="End date must be after start date"):
        vacation_facade.create_vacation(
            country_code="US",
            destination="Test",
            description="Test",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=1),
            price=Decimal("100.00")
        )


def test_get_vacation(vacation_facade, test_vacation):
    """Test getting a vacation by ID."""
    vacation = vacation_facade.get_vacation(test_vacation['id'])
    assert vacation['id'] == test_vacation['id']
    assert vacation['destination'] == test_vacation['destination']


def test_get_vacation_with_likes(vacation_facade, test_vacation, test_user):
    """Test getting a vacation with like information."""
    # Like the vacation
    vacation_facade.like_vacation(test_user.id, test_vacation['id'])
    
    # Get vacation with like info
    vacation = vacation_facade.get_vacation(test_vacation['id'], test_user.id)
    assert vacation['is_liked'] is True
    assert vacation['likes_count'] == 1


def test_update_vacation(vacation_facade, test_vacation):
    """Test updating a vacation."""
    updated = vacation_facade.update_vacation(
        test_vacation['id'],
        destination="Updated Destination",
        price=Decimal("2000.00")
    )
    
    assert updated['destination'] == "Updated Destination"
    assert updated['price'] == Decimal("2000.00")
    assert updated['id'] == test_vacation['id']


def test_update_vacation_invalid_country(vacation_facade, test_vacation):
    """Test updating a vacation with invalid country code."""
    with pytest.raises(ValueError, match="Invalid country code: XX"):
        vacation_facade.update_vacation(
            test_vacation['id'],
            country_code="XX"
        )


def test_delete_vacation(vacation_facade, test_vacation):
    """Test deleting a vacation."""
    assert vacation_facade.delete_vacation(test_vacation['id']) is True
    
    with pytest.raises(ValueError, match="Vacation not found"):
        vacation_facade.get_vacation(test_vacation['id'])


def test_like_vacation(vacation_facade, test_vacation, test_user):
    """Test liking a vacation."""
    like = vacation_facade.like_vacation(test_user.id, test_vacation['id'])
    
    assert like['user_id'] == test_user.id
    assert like['vacation_id'] == test_vacation['id']
    assert 'created_at' in like


def test_like_vacation_already_liked(vacation_facade, test_vacation, test_user):
    """Test liking a vacation that's already liked."""
    vacation_facade.like_vacation(test_user.id, test_vacation['id'])
    
    with pytest.raises(ValueError, match="has already liked vacation"):
        vacation_facade.like_vacation(test_user.id, test_vacation['id'])


def test_unlike_vacation(vacation_facade, test_vacation, test_user):
    """Test unliking a vacation."""
    # First like it
    vacation_facade.like_vacation(test_user.id, test_vacation['id'])
    
    # Then unlike it
    assert vacation_facade.unlike_vacation(test_user.id, test_vacation['id']) is True
    
    # Verify it's unliked
    vacation = vacation_facade.get_vacation(test_vacation['id'], test_user.id)
    assert vacation['is_liked'] is False
    assert vacation['likes_count'] == 0


def test_unlike_vacation_not_liked(vacation_facade, test_vacation, test_user):
    """Test unliking a vacation that's not liked."""
    with pytest.raises(ValueError, match="has not liked vacation"):
        vacation_facade.unlike_vacation(test_user.id, test_vacation['id'])


def test_get_user_liked_vacations(vacation_facade, test_user):
    """Test getting vacations liked by a user."""
    # Create and like multiple vacations
    vacation1 = vacation_facade.create_vacation(
        country_code="US",
        destination="Destination 1",
        description="Description 1",
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=5),
        price=Decimal("100.00")
    )
    
    vacation2 = vacation_facade.create_vacation(
        country_code="GB",
        destination="Destination 2",
        description="Description 2",
        start_date=date.today() + timedelta(days=6),
        end_date=date.today() + timedelta(days=10),
        price=Decimal("200.00")
    )
    
    vacation_facade.like_vacation(test_user.id, vacation1['id'])
    vacation_facade.like_vacation(test_user.id, vacation2['id'])
    
    # Get liked vacations
    liked_vacations = vacation_facade.get_user_liked_vacations(test_user.id)
    
    assert len(liked_vacations) == 2
    assert all(v['is_liked'] for v in liked_vacations)
    assert {v['id'] for v in liked_vacations} == {vacation1['id'], vacation2['id']}


def test_get_popular_vacations(vacation_facade, test_user):
    """Test getting popular vacations."""
    # Create multiple vacations with different like counts
    vacation1 = vacation_facade.create_vacation(
        country_code="US",
        destination="Popular Destination",
        description="Most liked",
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=5),
        price=Decimal("100.00")
    )
    
    vacation2 = vacation_facade.create_vacation(
        country_code="GB",
        destination="Less Popular",
        description="Less liked",
        start_date=date.today() + timedelta(days=6),
        end_date=date.today() + timedelta(days=10),
        price=Decimal("200.00")
    )
    
    # Create additional test users and like vacations
    users = []
    for i in range(3):
        user = User(
            first_name=f"Test{i}",
            last_name="User",
            email=f"test{i}@example.com",
            password="password123"
        )
        users.append(UserService.create(user))
    
    # More likes for vacation1
    for user in users:
        vacation_facade.like_vacation(user.id, vacation1['id'])
    
    # Fewer likes for vacation2
    vacation_facade.like_vacation(users[0].id, vacation2['id'])
    
    # Get popular vacations
    popular = vacation_facade.get_popular_vacations(limit=2)
    
    assert len(popular) == 2
    assert popular[0]['id'] == vacation1['id']
    assert popular[0]['likes_count'] == 3
    assert popular[1]['id'] == vacation2['id']
    assert popular[1]['likes_count'] == 1


def test_search_vacations(vacation_facade, test_user):
    """Test searching vacations with filters."""
    # Create test vacations
    vacation1 = vacation_facade.create_vacation(
        country_code="US",
        destination="New York",
        description="City break",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=15),
        price=Decimal("1000.00")
    )
    
    vacation2 = vacation_facade.create_vacation(
        country_code="GB",
        destination="London",
        description="City exploration",
        start_date=date.today() + timedelta(days=20),
        end_date=date.today() + timedelta(days=25),
        price=Decimal("1500.00")
    )
    
    # Like one vacation
    vacation_facade.like_vacation(test_user.id, vacation1['id'])
    
    # Search with various filters
    results = vacation_facade.search_vacations(
        query="City",
        min_price=Decimal("800.00"),
        max_price=Decimal("1200.00"),
        user_id=test_user.id
    )
    
    assert len(results) == 1
    assert results[0]['id'] == vacation1['id']
    assert results[0]['is_liked'] is True
    
    # Search by country
    results = vacation_facade.search_vacations(country_code="GB")
    assert len(results) == 1
    assert results[0]['id'] == vacation2['id']
    
    # Search by date range
    results = vacation_facade.search_vacations(
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=18)
    )
    assert len(results) == 1
    assert results[0]['id'] == vacation1['id']
