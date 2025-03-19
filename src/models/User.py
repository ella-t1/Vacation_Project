"""
User model with password hashing and validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import bcrypt

class User:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str = None,
        role_id: str = 'user',
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role_id = role_id
        self.created_at = created_at or datetime.now()
        self._password = None
        if password:
            self.set_password(password)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def password_hash(self) -> Optional[str]:
        """Get hashed password."""
        return self._password

    @property
    def password(self) -> Optional[str]:
        """Get hashed password."""
        return self._password

    @password.setter
    def password(self, value: str):
        """Set password with automatic hashing."""
        if value:
            self.set_password(value)

    def set_password(self, password: str):
        """Hash and set the password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self._password = hashed.decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self._password:
            return False
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self._password.encode('utf-8')
            )
        except ValueError:
            return False

    def to_dict(self) -> Dict:
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role_id': self.role_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create a User instance from a dictionary."""
        created_at = data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif not isinstance(created_at, datetime):
                created_at = None

        user = cls(
            id=data.get('id'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            role_id=data.get('role_id', 'user'),
            created_at=created_at
        )
        user._password = data.get('password')
        return user

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'User':
        """
        Create a User instance from a database row.
        
        Args:
            row: Dictionary containing user data from database
            
        Returns:
            User instance
        """
        if not row:
            return None
            
        user = cls(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            role_id=row['role_id'],
            created_at=row['created_at']
        )
        user._password = row['password']  # Store the hashed password from DB
        return user

    def __eq__(self, other: object) -> bool:
        """Compare two user objects."""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        """String representation of user."""
        return f"User(id={self.id}, email={self.email}, full_name={self.full_name})" 