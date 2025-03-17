from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'

class User:
    def __init__(
        self,
        id: int,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role_id: UserRole = UserRole.USER,
        created_at: Optional[str] = None
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role_id = role_id
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            role_id=UserRole(data['role_id']),
            created_at=data.get('created_at')
        )