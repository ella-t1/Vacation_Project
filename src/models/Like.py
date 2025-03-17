from typing import Optional

class Like:
    def __init__(
        self,
        id: int,
        user_id: int,
        vacation_id: int,
        created_at: Optional[str] = None
    ):
        self.id = id
        self.user_id = user_id
        self.vacation_id = vacation_id
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict) -> 'Like':
        """Create a Like instance from a dictionary."""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            vacation_id=data['vacation_id'],
            created_at=data.get('created_at')
        )
