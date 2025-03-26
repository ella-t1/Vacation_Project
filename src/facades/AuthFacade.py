"""
Authentication facade that provides a high-level interface for authentication operations.
"""
from typing import Dict, Tuple, Optional
from src.dal.AuthService import AuthService
from src.dal.UserService import UserService


class AuthFacade:
    """
    Facade for authentication operations.
    Provides a high-level interface for user authentication, registration,
    and password management.
    """
    
    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str
    ) -> Tuple[Dict, str]:
        """
        Register a new user.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (user dictionary, JWT token)
            
        Raises:
            ValueError: If email is already registered
        """
        user = AuthService.register(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        _, token = AuthService.login(email, password)
        return user.to_dict(), token

    def login(self, email: str, password: str) -> Tuple[Dict, str]:
        """
        Authenticate a user and generate a JWT token.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (user dictionary, JWT token)
            
        Raises:
            ValueError: If credentials are invalid
        """
        user, token = AuthService.login(email, password)
        return user.to_dict(), token

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User dictionary if token is valid, None otherwise
        """
        user = AuthService.verify_token(token)
        return user.to_dict() if user else None

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: ID of the user
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValueError: If old password is incorrect
        """
        return AuthService.change_password(user_id, old_password, new_password)

    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Request a password reset for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Reset token if user exists, None otherwise
        """
        return AuthService.request_password_reset(email)

    def reset_password(self, reset_token: str, new_password: str) -> bool:
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
        return AuthService.reset_password(reset_token, new_password)

    def refresh_token(self, token: str) -> str:
        """
        Generate a new token for a user with extended expiry.
        
        Args:
            token: Current valid JWT token
            
        Returns:
            New JWT token with extended expiry
            
        Raises:
            ValueError: If token is invalid or expired
        """
        return AuthService.refresh_token(token) 