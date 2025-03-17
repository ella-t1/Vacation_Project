import pytest
from datetime import datetime
from src.models.User import User, UserRole
from src.models.Like import Like
from src.dal.UserManagement import UserManagement
from src.dal.query import hash_password

@pytest.fixture
def user_management():
    return UserManagement()

@pytest.fixture
def valid_user():
    return User(
        id=0,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password=hash_password("password123"),
        role_id=UserRole.USER
    )

@pytest.fixture
def valid_like():
    return Like(
        id=0,
        user_id=1,
        vacation_id=1
    )

class TestUserValidation:
    def test_valid_email(self, user_management):
        assert user_management._validate_email("test@example.com") is True
        assert user_management._validate_email("user.name@domain.co.uk") is True
        assert user_management._validate_email("user+tag@example.com") is True

    def test_invalid_email(self, user_management):
        assert user_management._validate_email("") is False
        assert user_management._validate_email("invalid") is False
        assert user_management._validate_email("@example.com") is False
        assert user_management._validate_email("test@") is False
        assert user_management._validate_email("test@.com") is False

    def test_valid_password(self, user_management):
        assert user_management._validate_password("password123") is True
        assert user_management._validate_password("Pass1234") is True
        assert user_management._validate_password("12345678a") is True

    def test_invalid_password(self, user_management):
        assert user_management._validate_password("") is False
        assert user_management._validate_password("1234567") is False  # too short
        assert user_management._validate_password("password") is False  # no numbers
        assert user_management._validate_password("12345678") is False  # no letters

    def test_valid_name(self, user_management):
        assert user_management._validate_name("John") is True
        assert user_management._validate_name("Mary") is True
        assert user_management._validate_name("O'Connor") is True

    def test_invalid_name(self, user_management):
        assert user_management._validate_name("") is False
        assert user_management._validate_name("J") is False  # too short
        assert user_management._validate_name("John123") is False  # contains numbers
        assert user_management._validate_name("John Doe") is False  # contains space

    def test_valid_user(self, user_management, valid_user):
        is_valid, error = user_management._validate_user(valid_user)
        assert is_valid is True
        assert error == ""

    def test_invalid_user(self, user_management):
        # Test with invalid email
        invalid_user = User(
            id=0,
            first_name="John",
            last_name="Doe",
            email="invalid-email",
            password=hash_password("password123"),
            role_id=UserRole.USER
        )
        is_valid, error = user_management._validate_user(invalid_user)
        assert is_valid is False
        assert "Invalid email format" in error

        # Test with invalid password
        invalid_user = User(
            id=0,
            first_name="John",
            last_name="Doe",
            email="test@example.com",
            password="weak",
            role_id=UserRole.USER
        )
        is_valid, error = user_management._validate_user(invalid_user)
        assert is_valid is False
        assert "Password must be at least 8 characters" in error

        # Test with invalid first name
        invalid_user = User(
            id=0,
            first_name="J",
            last_name="Doe",
            email="test@example.com",
            password=hash_password("password123"),
            role_id=UserRole.USER
        )
        is_valid, error = user_management._validate_user(invalid_user)
        assert is_valid is False
        assert "Invalid first name" in error

class TestUserManagement:
    def test_add_new_user(self, user_management, valid_user):
        # Test adding a valid user
        new_user = user_management.add_new_user(valid_user)
        assert new_user is not None
        assert new_user.id > 0
        assert new_user.email == valid_user.email.lower()
        assert new_user.first_name == valid_user.first_name.strip()
        assert new_user.last_name == valid_user.last_name.strip()

        # Test adding duplicate email
        with pytest.raises(ValueError, match="Email already exists"):
            user_management.add_new_user(valid_user)

    def test_get_user(self, user_management, valid_user):
        # First add a user
        user_management.add_new_user(valid_user)

        # Test getting user with correct credentials
        user = user_management.get_user(valid_user.email, valid_user.password)
        assert user is not None
        assert user.email == valid_user.email.lower()

        # Test getting user with wrong password
        user = user_management.get_user(valid_user.email, "wrongpassword")
        assert user is None

        # Test getting user with invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            user_management.get_user("invalid-email", valid_user.password)

    def test_is_email_exist(self, user_management, valid_user):
        # First add a user
        user_management.add_new_user(valid_user)

        # Test existing email
        assert user_management.is_email_exist(valid_user.email) is True

        # Test non-existing email
        assert user_management.is_email_exist("nonexistent@example.com") is False

        # Test invalid email format
        with pytest.raises(ValueError, match="Invalid email format"):
            user_management.is_email_exist("invalid-email")

    def test_like_operations(self, user_management, valid_like):
        # Test adding a like
        assert user_management.add_like(valid_like) is True

        # Test getting user likes
        likes = user_management.get_user_likes(valid_like.user_id)
        assert valid_like.vacation_id in likes

        # Test removing a like
        assert user_management.remove_like(valid_like) is True

        # Verify like was removed
        likes = user_management.get_user_likes(valid_like.user_id)
        assert valid_like.vacation_id not in likes

        # Test invalid like object
        with pytest.raises(ValueError, match="Invalid like object"):
            user_management.add_like(None)

        # Test invalid user_id
        with pytest.raises(ValueError, match="Invalid user_id"):
            user_management.get_user_likes(0) 