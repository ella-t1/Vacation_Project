from datetime import datetime
from typing import Optional, Dict

class Country:
    def __init__(
        self,
        name: str,
        code: str,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a Country instance.
        
        Args:
            name: Full name of the country
            code: Two-letter ISO country code
            id: Database ID (optional)
            created_at: Creation timestamp (optional)
        """
        self.id = id
        self.name = name
        self.code = self._validate_code(code)
        self.created_at = created_at or datetime.now()

    @staticmethod
    def _validate_code(code: str) -> str:
        """
        Validate and normalize country code.
        
        Args:
            code: Two-letter ISO country code
            
        Returns:
            Normalized (uppercase) country code
            
        Raises:
            ValueError: If code is not valid
        """
        if not code or not isinstance(code, str):
            raise ValueError("Country code must be a string")
        
        code = code.strip().upper()
        if len(code) != 2:
            raise ValueError("Country code must be exactly 2 characters")
            
        if not code.isalpha():
            raise ValueError("Country code must contain only letters")
            
        return code

    def to_dict(self) -> Dict:
        """
        Convert country object to dictionary.
        
        Returns:
            Dictionary representation of the country
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Country':
        """
        Create a Country instance from a dictionary.
        
        Args:
            data: Dictionary containing country data
            
        Returns:
            New Country instance
        """
        created_at = data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif not isinstance(created_at, datetime):
                created_at = None

        return cls(
            id=data.get('id'),
            name=data['name'],
            code=data['code'],
            created_at=created_at
        )

    def __eq__(self, other: object) -> bool:
        """Compare two country objects."""
        if not isinstance(other, Country):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        """String representation of country."""
        return f"Country(id={self.id}, name={self.name}, code={self.code})" 