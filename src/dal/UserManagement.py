from typing import Optional, List
from src.models.Like import Like
from src.models.User import User, UserRole
from src.dal.query import query, hash_password
import re

class UserManagement:
    def __init__(self):
        # Email validation regex pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Password requirements
        self.min_password_length = 8
        self.password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(self.email_pattern.match(email))

    def _validate_password(self, password: str) -> bool:
        """Validate password strength."""
        if not password or not isinstance(password, str):
            return False
        if len(password) < self.min_password_length:
            return False
        return bool(self.password_pattern.match(password))

    def _validate_name(self, name: str) -> bool:
        """Validate name format."""
        if not name or not isinstance(name, str):
            return False
        return len(name.strip()) >= 2 and name.strip().isalpha()

    def _validate_user(self, user: User) -> tuple[bool, str]:
        """Validate all user fields."""
        if not isinstance(user, User):
            return False, "Invalid user object"
        
        if not self._validate_email(user.email):
            return False, "Invalid email format"
        
        if not self._validate_password(user.password):
            return False, "Password must be at least 8 characters and contain both letters and numbers"
        
        if not self._validate_name(user.first_name):
            return False, "Invalid first name"
        
        if not self._validate_name(user.last_name):
            return False, "Invalid last name"
        
        if not isinstance(user.role_id, UserRole):
            return False, "Invalid role"
        
        return True, ""

    def add_new_user(self, new_user: User) -> Optional[User]:
        """
        Add a new user to the database.
        Returns the created user with its ID if successful, None otherwise.
        """
        try:
            # Validate user data
            is_valid, error_message = self._validate_user(new_user)
            if not is_valid:
                raise ValueError(error_message)

            # Check if email already exists
            if self.is_email_exist(new_user.email):
                raise ValueError("Email already exists")

            result = query("""
                INSERT INTO users (first_name, last_name, email, password, role_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, first_name, last_name, email, password, role_id, created_at
            """, (
                new_user.first_name.strip(),
                new_user.last_name.strip(),
                new_user.email.lower(),
                new_user.password,
                new_user.role_id.value
            ), fetch=True)
            
            if result:
                return User.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error adding new user: {e}")
            raise

    def get_user(self, email: str, password: str) -> Optional[User]:
        """
        Get a user by email and password.
        Returns the user if found and password matches, None otherwise.
        """
        try:
            # Validate input
            if not self._validate_email(email):
                raise ValueError("Invalid email format")
            if not self._validate_password(password):
                raise ValueError("Invalid password format")

            result = query("""
                SELECT id, first_name, last_name, email, password, role_id, created_at
                FROM users
                WHERE email = %s AND password = %s
            """, (email.lower(), password), fetch=True)
            
            if result:
                return User.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            raise

    def is_email_exist(self, email: str) -> bool:
        """Check if an email already exists in the database."""
        try:
            # Validate email format
            if not self._validate_email(email):
                raise ValueError("Invalid email format")

            result = query("""
                SELECT 1
                FROM users
                WHERE email = %s
            """, (email.lower(),), fetch=True)
            
            return bool(result)
            
        except Exception as e:
            print(f"Error checking email existence: {e}")
            raise

    def add_like(self, like: Like) -> bool:
        """Add a like to the database."""
        try:
            # Validate like object
            if not isinstance(like, Like):
                raise ValueError("Invalid like object")
            if not like.user_id or not like.vacation_id:
                raise ValueError("Invalid user_id or vacation_id")

            query("""
                INSERT INTO likes (user_id, vacation_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, vacation_id) DO NOTHING
            """, (like.user_id, like.vacation_id), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error adding like: {e}")
            raise

    def remove_like(self, like: Like) -> bool:
        """Remove a like from the database."""
        try:
            # Validate like object
            if not isinstance(like, Like):
                raise ValueError("Invalid like object")
            if not like.user_id or not like.vacation_id:
                raise ValueError("Invalid user_id or vacation_id")

            query("""
                DELETE FROM likes
                WHERE user_id = %s AND vacation_id = %s
            """, (like.user_id, like.vacation_id), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error removing like: {e}")
            raise

    def get_user_likes(self, user_id: int) -> List[int]:
        """Get all vacation IDs that a user has liked."""
        try:
            # Validate user_id
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("Invalid user_id")

            result = query("""
                SELECT vacation_id
                FROM likes
                WHERE user_id = %s
            """, (user_id,), fetch=True)
            
            return [row['vacation_id'] for row in result]
            
        except Exception as e:
            print(f"Error getting user likes: {e}")
            raise