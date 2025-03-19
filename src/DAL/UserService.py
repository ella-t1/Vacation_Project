"""
User service that handles user data operations.
"""
from typing import Optional, List
from src.models.User import User
from src.query import query


class UserService:
    @staticmethod
    def create(user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User instance to create
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If user with email already exists
        """
        # Check if email exists
        if UserService.get_by_email(user.email):
            raise ValueError("Email already exists")
        
        # Insert user
        sql = """
        INSERT INTO users (first_name, last_name, email, password, role_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, first_name, last_name, email, password, role_id, created_at
        """
        params = [
            user.first_name,
            user.last_name,
            user.email,
            user.password_hash,  # We store the hash in the password column
            user.role_id
        ]
        result = query(sql, params, commit=True)
        return User.from_db_row(result[0])

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance if found, None otherwise
        """
        sql = """
        SELECT id, first_name, last_name, email, password, role_id, created_at
        FROM users
        WHERE id = %s
        """
        result = query(sql, [user_id])
        return User.from_db_row(result[0]) if result else None

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User instance if found, None otherwise
        """
        sql = """
        SELECT id, first_name, last_name, email, password, role_id, created_at
        FROM users
        WHERE email = %s
        """
        result = query(sql, [email])
        return User.from_db_row(result[0]) if result else None

    @staticmethod
    def update(user: User) -> User:
        """
        Update a user.
        
        Args:
            user: User instance to update
            
        Returns:
            Updated user instance
            
        Raises:
            ValueError: If user not found
        """
        sql = """
        UPDATE users
        SET first_name = %s,
            last_name = %s,
            email = %s,
            role_id = %s
        WHERE id = %s
        RETURNING id, first_name, last_name, email, password, role_id, created_at
        """
        params = [
            user.first_name,
            user.last_name,
            user.email,
            user.role_id,
            user.id
        ]
        result = query(sql, params, commit=True)
        if not result:
            raise ValueError("User not found")
        return User.from_db_row(result[0])

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: User ID
            new_password: New password (will be hashed)
            
        Returns:
            True if password was updated
            
        Raises:
            ValueError: If user not found
        """
        # Get user to generate new password hash
        user = UserService.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update password hash
        user.set_password(new_password)
        sql = """
        UPDATE users
        SET password = %s
        WHERE id = %s
        """
        query(sql, [user.password_hash, user_id], commit=True)
        return True

    @staticmethod
    def delete(user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deleted
        """
        sql = "DELETE FROM users WHERE id = %s"
        query(sql, [user_id], commit=True)
        return True

    @staticmethod
    def get_all() -> List[User]:
        """
        Get all users.
        
        Returns:
            List of user instances
        """
        sql = """
        SELECT id, first_name, last_name, email, password, role_id, created_at
        FROM users
        ORDER BY created_at DESC
        """
        result = query(sql)
        return [User.from_db_row(row) for row in result]

    @staticmethod
    def exists(email: str) -> bool:
        """
        Check if a user with the given email exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if user exists
        """
        sql = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)"
        result = query(sql, [email])
        return result[0]['exists']

    @staticmethod
    def count() -> int:
        """
        Get total number of users.
        
        Returns:
            Total number of users
        """
        sql = "SELECT COUNT(*) as count FROM users"
        result = query(sql)
        return result[0]['count']

    @staticmethod
    def _execute_query(sql: str, params: list = None) -> None:
        """Execute a raw SQL query. For testing purposes only."""
        query(sql, params, commit=True) 