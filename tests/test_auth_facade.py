"""Tests for the AuthFacade class."""
import pytest
from datetime import datetime
from src.facades.AuthFacade import AuthFacade
from src.models.User import User
from src.DAL.UserService import UserService
from src.query import query
from src.config import get_test_config


@pytest.fixture
def auth_facade(setup_test_db):
    """Create AuthFacade instance."""
    return AuthFacade()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        'first_name': 'Test',
        'last_name': 'User',
        'email': f'test{datetime.now().timestamp()}@test.com',
        'password': 'TestPass123!'
    }


def test_register_success(auth_facade, test_user_data):
    """Test successful user registration."""
    # Register user
    user_dict, token = auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Verify user data
    assert user_dict['email'] == test_user_data['email']
    assert user_dict['first_name'] == test_user_data['first_name']
    assert user_dict['last_name'] == test_user_data['last_name']
    assert user_dict['role_id'] == 'user'
    assert 'id' in user_dict
    assert 'created_at' in user_dict
    
    # Verify token
    user_data = auth_facade.verify_token(token)
    assert user_data is not None
    assert user_data['email'] == test_user_data['email']


def test_register_duplicate_email(auth_facade, test_user_data):
    """Test registration with duplicate email."""
    # Register first user
    auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Try to register with same email
    with pytest.raises(ValueError, match="Email already registered"):
        auth_facade.register(
            first_name='Another',
            last_name='User',
            email=test_user_data['email'],
            password='DifferentPass123!'
        )


def test_login_success(auth_facade, test_user_data):
    """Test successful login."""
    # Register user
    auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Login
    user_dict, token = auth_facade.login(
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Verify user data and token
    assert user_dict['email'] == test_user_data['email']
    assert user_dict['first_name'] == test_user_data['first_name']
    assert user_dict['last_name'] == test_user_data['last_name']
    
    # Verify token
    user_data = auth_facade.verify_token(token)
    assert user_data is not None
    assert user_data['email'] == test_user_data['email']


def test_login_invalid_email(auth_facade):
    """Test login with invalid email."""
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_facade.login(
            email="nonexistent@test.com",
            password="AnyPassword123!"
        )


def test_login_invalid_password(auth_facade, test_user_data):
    """Test login with invalid password."""
    # Register user
    auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Try to login with wrong password
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_facade.login(
            email=test_user_data['email'],
            password='WrongPass123!'
        )


def test_verify_token_success(auth_facade, test_user_data):
    """Test successful token verification."""
    # Register user and get token
    _, token = auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Verify token
    user_data = auth_facade.verify_token(token)
    assert user_data is not None
    assert user_data['email'] == test_user_data['email']
    assert user_data['first_name'] == test_user_data['first_name']
    assert user_data['last_name'] == test_user_data['last_name']


def test_verify_token_invalid(auth_facade):
    """Test verification of invalid token."""
    user_data = auth_facade.verify_token('invalid.token.here')
    assert user_data is None


def test_change_password_success(auth_facade, test_user_data):
    """Test successful password change."""
    # Register user
    user_dict, _ = auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Change password
    new_password = 'NewPass123!'
    result = auth_facade.change_password(
        user_id=user_dict['id'],
        old_password=test_user_data['password'],
        new_password=new_password
    )
    assert result is True
    
    # Verify can login with new password
    user_dict, token = auth_facade.login(
        email=test_user_data['email'],
        password=new_password
    )
    assert user_dict is not None
    assert token is not None


def test_change_password_incorrect_old(auth_facade, test_user_data):
    """Test password change with incorrect old password."""
    # Register user
    user_dict, _ = auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Try to change password with wrong old password
    with pytest.raises(ValueError, match="Current password is incorrect"):
        auth_facade.change_password(
            user_id=user_dict['id'],
            old_password='WrongPass123!',
            new_password='NewPass123!'
        )


def test_password_reset_flow(auth_facade, test_user_data):
    """Test complete password reset flow."""
    # Register user
    auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Request password reset
    reset_token = auth_facade.request_password_reset(test_user_data['email'])
    assert reset_token is not None
    
    # Reset password
    new_password = 'ResetPass123!'
    result = auth_facade.reset_password(reset_token, new_password)
    assert result is True
    
    # Verify can login with new password
    user_dict, token = auth_facade.login(
        email=test_user_data['email'],
        password=new_password
    )
    assert user_dict is not None
    assert token is not None


def test_password_reset_invalid_token(auth_facade):
    """Test password reset with invalid token."""
    with pytest.raises(ValueError, match="Invalid or expired reset token"):
        auth_facade.reset_password(
            reset_token='invalid.token.here',
            new_password='NewPass123!'
        )


def test_refresh_token(auth_facade, test_user_data):
    """Test token refresh."""
    # Register user and get token
    _, token = auth_facade.register(
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        email=test_user_data['email'],
        password=test_user_data['password']
    )
    
    # Refresh token
    new_token = auth_facade.refresh_token(token)
    assert new_token is not None
    assert new_token != token
    
    # Verify new token is valid
    user_data = auth_facade.verify_token(new_token)
    assert user_data is not None
    assert user_data['email'] == test_user_data['email']


def test_refresh_token_invalid(auth_facade):
    """Test token refresh with invalid token."""
    with pytest.raises(ValueError, match="Invalid or expired token"):
        auth_facade.refresh_token('invalid.token.here') 