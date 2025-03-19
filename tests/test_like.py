"""
Tests for the Like model and service.
"""
import pytest
from datetime import datetime
from src.models.Like import Like
from src.DAL.LikeService import LikeService
from src.models.User import User
from src.models.Vacation import Vacation
from src.models.Country import Country
from src.DAL.UserService import UserService
from src.DAL.VacationService import VacationService
from src.DAL.CountryService import CountryService
from src.config import get_test_config
from src.query import init_pool, close_pool, query


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database connection."""
    config, _ = get_test_config()
    init_pool(config)
    yield
    close_pool()


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test data after each test."""
    yield
    # Clean up any test data
    query("DELETE FROM likes", commit=True)
    query("DELETE FROM vacations", commit=True)
    query("DELETE FROM users WHERE email LIKE 'test%@example.com'", commit=True)
    query("DELETE FROM countries WHERE code LIKE 'T%'", commit=True)


@pytest.fixture
def setup_db():
    """Set up test database."""
    # Create test data with unique email
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    user = User(
        first_name="Test",
        last_name="User",
        email=f"test{timestamp}@example.com",
        password="password123"
    )
    user = UserService.create(user)

    country = Country(
        name='Test Country',
        code=f'T{chr(65 + (int(timestamp[-2:]) % 26))}'  # Use T + letter (A-Z)
    )
    country = CountryService.create(country)

    vacation = Vacation(
        country_id=country.id,
        destination="Test Destination",
        description="Test Description",
        start_date=datetime.now().date(),
        end_date=datetime.now().date(),
        price=100.00,
        image_url="test.jpg"
    )
    vacation = VacationService.create(vacation)

    yield {
        'user': user,
        'vacation': vacation,
        'country': country
    }

    # Cleanup
    try:
        UserService.delete(user.id)
        VacationService.delete(vacation.id)
        CountryService.delete(country.id)
    except:
        pass


def test_like_creation():
    """Test creating a Like instance."""
    like = Like(user_id=1, vacation_id=1)
    
    assert like.user_id == 1
    assert like.vacation_id == 1
    assert like.id is None
    assert isinstance(like.created_at, datetime)


def test_like_to_dict():
    """Test converting Like to dictionary."""
    now = datetime.now()
    like = Like(
        id=1,
        user_id=1,
        vacation_id=1,
        created_at=now
    )
    
    data = like.to_dict()
    assert data['id'] == 1
    assert data['user_id'] == 1
    assert data['vacation_id'] == 1
    assert data['created_at'] == now.isoformat()


def test_like_from_dict():
    """Test creating Like from dictionary."""
    now = datetime.now()
    data = {
        'id': 1,
        'user_id': 1,
        'vacation_id': 1,
        'created_at': now.isoformat()
    }
    
    like = Like.from_dict(data)
    assert like.id == 1
    assert like.user_id == 1
    assert like.vacation_id == 1
    assert like.created_at == now


def test_create_like(setup_db):
    """Test creating a like."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    created_like = LikeService.create(like)
    
    assert created_like.id is not None
    assert created_like.user_id == like.user_id
    assert created_like.vacation_id == like.vacation_id


def test_create_duplicate_like(setup_db):
    """Test creating a duplicate like."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    with pytest.raises(ValueError) as exc:
        LikeService.create(like)
    assert "already liked" in str(exc.value)


def test_delete_like(setup_db):
    """Test deleting a like."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    created_like = LikeService.create(like)
    
    assert LikeService.delete(created_like.user_id, created_like.vacation_id)
    assert not LikeService.has_user_liked(created_like.user_id, created_like.vacation_id)


def test_get_by_user(setup_db):
    """Test getting vacations liked by user."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    likes = LikeService.get_by_user(setup_db['user'].id)
    assert len(likes) == 1
    assert likes[0]['id'] == setup_db['vacation'].id


def test_get_by_vacation(setup_db):
    """Test getting users who liked a vacation."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    likes = LikeService.get_by_vacation(setup_db['vacation'].id)
    assert len(likes) == 1
    assert likes[0]['id'] == setup_db['user'].id


def test_count_by_vacation(setup_db):
    """Test counting likes for a vacation."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    count = LikeService.count_by_vacation(setup_db['vacation'].id)
    assert count == 1


def test_has_user_liked(setup_db):
    """Test checking if user has liked a vacation."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    assert LikeService.has_user_liked(setup_db['user'].id, setup_db['vacation'].id)
    assert not LikeService.has_user_liked(999, setup_db['vacation'].id)


def test_get_popular_vacations(setup_db):
    """Test getting popular vacations."""
    like = Like(
        user_id=setup_db['user'].id,
        vacation_id=setup_db['vacation'].id
    )
    LikeService.create(like)
    
    popular = LikeService.get_popular_vacations(limit=1)
    assert len(popular) == 1
    assert popular[0]['id'] == setup_db['vacation'].id
    assert popular[0]['like_count'] == 1 