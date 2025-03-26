"""
Tests for the AuthService class.
"""
import pytest
from datetime import datetime, timedelta, UTC
import jwt
from src.dal.AuthService import AuthService
from src.models.User import User


def test_register_success():
    """Test successful user registration."""
    user = AuthService.register(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123"
    )
    
    assert user.id is not None
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.verify_password("password123")


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    email = "duplicate@example.com"
    
    # Register first user
    AuthService.register(
        first_name="First",
        last_name="User",
        email=email,
        password="password123"
    )
    
    # Try to register second user with same email
    with pytest.raises(ValueError, match="Email already registered"):
        AuthService.register(
            first_name="Second",
            last_name="User",
            email=email,
            password="password456"
        )


def test_login_success():
    """Test successful login."""
    # Register user
    email = "login.test@example.com"
    password = "password123"
    AuthService.register(
        first_name="Login",
        last_name="Test",
        email=email,
        password=password
    )
    
    # Login
    user, token = AuthService.login(email, password)
    
    assert user is not None
    assert user.email == email
    assert token is not None
    
    # Verify token
    decoded = jwt.decode(
        token,
        AuthService.JWT_SECRET,
        algorithms=[AuthService.JWT_ALGORITHM]
    )
    assert decoded['sub'] == user.id
    assert decoded['email'] == user.email
    assert decoded['role_id'] == user.role_id


def test_login_invalid_email():
    """Test login with invalid email."""
    with pytest.raises(ValueError, match="Invalid email or password"):
        AuthService.login("nonexistent@example.com", "password123")


def test_login_invalid_password():
    """Test login with invalid password."""
    # Register user
    email = "password.test@example.com"
    AuthService.register(
        first_name="Password",
        last_name="Test",
        email=email,
        password="correct_password"
    )
    
    # Try to login with wrong password
    with pytest.raises(ValueError, match="Invalid email or password"):
        AuthService.login(email, "wrong_password")


def test_verify_token_success():
    """Test successful token verification."""
    # Register and login user
    email = "token.test@example.com"
    user = AuthService.register(
        first_name="Token",
        last_name="Test",
        email=email,
        password="password123"
    )
    
    _, token = AuthService.login(email, "password123")
    
    # Verify token
    verified_user = AuthService.verify_token(token)
    assert verified_user is not None
    assert verified_user.id == user.id
    assert verified_user.email == user.email


def test_verify_token_invalid():
    """Test verification of invalid token."""
    invalid_token = "invalid.token.here"
    assert AuthService.verify_token(invalid_token) is None


def test_verify_token_expired():
    """Test verification of expired token."""
    # Register user
    email = "expired.test@example.com"
    user = AuthService.register(
        first_name="Expired",
        last_name="Test",
        email=email,
        password="password123"
    )
    
    # Generate expired token
    now = datetime.now(UTC)
    payload = {
        'sub': user.id,
        'email': user.email,
        'role_id': user.role_id,
        'iat': now - timedelta(hours=25),
        'exp': now - timedelta(hours=1)
    }
    expired_token = jwt.encode(
        payload,
        AuthService.JWT_SECRET,
        algorithm=AuthService.JWT_ALGORITHM
    )
    
    assert AuthService.verify_token(expired_token) is None


def test_change_password_success():
    """Test successful password change."""
    # Register user
    email = "change.password@example.com"
    old_password = "old_password"
    new_password = "new_password"
    
    user = AuthService.register(
        first_name="Change",
        last_name="Password",
        email=email,
        password=old_password
    )
    
    # Change password
    assert AuthService.change_password(user.id, old_password, new_password) is True
    
    # Verify old password no longer works
    with pytest.raises(ValueError):
        AuthService.login(email, old_password)
    
    # Verify new password works
    user, _ = AuthService.login(email, new_password)
    assert user is not None
    assert user.email == email


def test_change_password_incorrect_old():
    """Test password change with incorrect old password."""
    # Register user
    email = "wrong.old@example.com"
    user = AuthService.register(
        first_name="Wrong",
        last_name="Old",
        email=email,
        password="correct_password"
    )
    
    # Try to change password with wrong old password
    with pytest.raises(ValueError, match="Current password is incorrect"):
        AuthService.change_password(user.id, "wrong_password", "new_password")


def test_reset_password_request():
    """Test password reset request."""
    # Register user
    email = "reset.test@example.com"
    AuthService.register(
        first_name="Reset",
        last_name="Test",
        email=email,
        password="password123"
    )
    
    # Request password reset
    assert AuthService.request_password_reset(email) is not None
    
    # Request for non-existent email should return None
    assert AuthService.request_password_reset("nonexistent@example.com") is None 