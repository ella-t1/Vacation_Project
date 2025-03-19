"""
Authentication service that handles JWT token generation and verification.
"""
import os
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta, UTC
import jwt
from src.models.User import User
from src.DAL.UserService import UserService


class AuthService:
    # Default values for JWT configuration
    JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
    JWT_ALGORITHM = 'HS256'

    @classmethod
    def register(cls, first_name: str, last_name: str, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
            password: User's password (will be hashed)
            
        Returns:
            The created User object
            
        Raises:
            ValueError: If the email is already registered
        """
        if UserService.exists(email):
            raise ValueError("Email already registered")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password  # Password will be hashed by the User model
        )
        
        return UserService.create(user)

    @classmethod
    def login(cls, email: str, password: str) -> Tuple[User, str]:
        """
        Authenticate a user and generate a JWT token.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (User object, JWT token)
            
        Raises:
            ValueError: If the credentials are invalid
        """
        user = UserService.get_by_email(email)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid email or password")

        token = cls.generate_token(user)
        return user, token

    @classmethod
    def generate_token(cls, user: User) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user: User instance to generate token for
            
        Returns:
            JWT token string
        """
        now = datetime.now(UTC)
        payload = {
            'sub': user.id,
            'email': user.email,
            'role_id': user.role_id,
            'iat': now,
            'exp': now + timedelta(hours=cls.JWT_EXPIRY_HOURS)
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> Optional[User]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User object if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, cls.JWT_SECRET, algorithms=[cls.JWT_ALGORITHM])
            print(f"Token payload: {payload}")  # Debug print
            
            user = UserService.get_by_id(payload['sub'])
            if not user:
                print("User not found")  # Debug print
                return None
            
            print(f"User: {user.to_dict()}")  # Debug print
            
            # Verify email and role match
            if user.email != payload['email']:
                print("Email mismatch")  # Debug print
                return None
                
            if user.role_id != payload['role_id']:
                print(f"Role mismatch: {user.role_id} != {payload['role_id']}")  # Debug print
                return None
                
            return user
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")  # Debug print
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")  # Debug print
            return None

    @classmethod
    def change_password(cls, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: ID of the user
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValueError: If the old password is incorrect
        """
        user = UserService.get_by_id(user_id)
        if not user or not user.verify_password(old_password):
            raise ValueError("Current password is incorrect")

        return UserService.update_password(user_id, new_password)

    @classmethod
    def request_password_reset(cls, email: str) -> Optional[str]:
        """
        Request a password reset for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Reset token if user exists, None otherwise
        """
        user = UserService.get_by_email(email)
        if not user:
            return None

        # Generate a short-lived reset token
        now = datetime.now(UTC)
        payload = {
            'sub': user.id,
            'email': user.email,
            'type': 'reset',
            'iat': now,
            'exp': now + timedelta(hours=1)  # Reset tokens expire in 1 hour
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def reset_password(cls, reset_token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.
        
        Args:
            reset_token: Password reset token
            new_password: New password to set
            
        Returns:
            True if password was reset successfully
            
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(reset_token, cls.JWT_SECRET, algorithms=[cls.JWT_ALGORITHM])
            
            # Verify it's a reset token
            if payload.get('type') != 'reset':
                raise ValueError("Invalid reset token")

            # Get user and verify email matches
            user = UserService.get_by_id(payload['sub'])
            if not user or user.email != payload['email']:
                raise ValueError("Invalid reset token")

            # Set new password
            return UserService.update_password(user.id, new_password)

        except jwt.InvalidTokenError:
            raise ValueError("Invalid or expired reset token")

    @classmethod
    def refresh_token(cls, token: str) -> str:
        """
        Generate a new token for a user with extended expiry.
        
        Args:
            token: Current valid JWT token
            
        Returns:
            New JWT token with extended expiry
            
        Raises:
            ValueError: If token is invalid or expired
        """
        user = cls.verify_token(token)
        if not user:
            raise ValueError("Invalid or expired token")

        # Generate new token with extended expiry
        now = datetime.now(UTC)
        payload = {
            'sub': user.id,
            'email': user.email,
            'role_id': user.role_id,
            'iat': now,
            'exp': now + timedelta(hours=cls.JWT_EXPIRY_HOURS),
            'jti': str(now.timestamp())  # Add a unique token ID
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM) 