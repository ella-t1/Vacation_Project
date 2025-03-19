from datetime import datetime
from typing import Optional, Dict


class Like:
    def __init__(
        self,
        user_id: int,
        vacation_id: int,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.vacation_id = vacation_id
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> Dict:
        """Convert like object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vacation_id': self.vacation_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Like':
        """Create a Like instance from a dictionary."""
        created_at = data.get('created_at')
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            vacation_id=data['vacation_id'],
            created_at=created_at
        )

    def __eq__(self, other: object) -> bool:
        """Compare two like objects."""
        if not isinstance(other, Like):
            return False
        return (
            self.id == other.id and
            self.user_id == other.user_id and
            self.vacation_id == other.vacation_id
        )

    def __str__(self) -> str:
        """String representation of like."""
        return f"Like(id={self.id}, user_id={self.user_id}, vacation_id={self.vacation_id})" 