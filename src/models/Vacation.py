from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict
from src.models.Country import Country

class Vacation:
    def __init__(
        self,
        country_id: int,
        destination: str,
        description: Optional[str],
        start_date: date,
        end_date: date,
        price: Decimal,
        image_url: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        country: Optional[Country] = None
    ):
        """
        Initialize a Vacation instance.
        
        Args:
            country_id: ID of the country where the vacation takes place
            destination: Name of the specific destination
            description: Detailed description of the vacation
            start_date: Start date of the vacation
            end_date: End date of the vacation
            price: Price of the vacation
            image_url: URL of the vacation image (optional)
            id: Database ID (optional)
            created_at: Creation timestamp (optional)
            country: Associated Country object (optional)
        """
        self.id = id
        self.country_id = country_id
        self.destination = self._validate_destination(destination)
        self.description = description
        self.start_date = self._validate_date(start_date)
        self.end_date = self._validate_date(end_date)
        self._validate_dates(self.start_date, self.end_date)
        self.price = self._validate_price(price)
        self.image_url = image_url
        self.created_at = created_at or datetime.now()
        self.country = country

    @staticmethod
    def _validate_destination(destination: str) -> str:
        """Validate destination name."""
        if not destination or not isinstance(destination, str):
            raise ValueError("Destination must be a non-empty string")
        destination = destination.strip()
        if len(destination) < 3:
            raise ValueError("Destination must be at least 3 characters long")
        return destination

    @staticmethod
    def _validate_date(value: date) -> date:
        """Convert and validate date."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        elif not isinstance(value, date):
            raise ValueError("Date must be a date object or YYYY-MM-DD string")
        return value

    @staticmethod
    def _validate_dates(start_date: date, end_date: date):
        """Validate date range."""
        if start_date > end_date:
            raise ValueError("End date must be after start date")
        if start_date < date.today():
            raise ValueError("Start date cannot be in the past")

    @staticmethod
    def _validate_price(price: Decimal) -> Decimal:
        """Validate price."""
        if isinstance(price, (int, float, str)):
            price = Decimal(str(price))
        if not isinstance(price, Decimal):
            raise ValueError("Price must be a decimal number")
        if price <= 0:
            raise ValueError("Price must be greater than zero")
        return round(price, 2)

    def to_dict(self) -> Dict:
        """
        Convert vacation object to dictionary.
        
        Returns:
            Dictionary representation of the vacation
        """
        return {
            'id': self.id,
            'country_id': self.country_id,
            'destination': self.destination,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'price': str(self.price),
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'country': self.country.to_dict() if self.country else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Vacation':
        """
        Create a Vacation instance from a dictionary.
        
        Args:
            data: Dictionary containing vacation data
            
        Returns:
            New Vacation instance
        """
        # Handle dates
        start_date = cls._validate_date(data['start_date'])
        end_date = cls._validate_date(data['end_date'])
        
        # Handle created_at
        created_at = data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif not isinstance(created_at, datetime):
                created_at = None
        
        # Handle country
        country_data = data.get('country')
        country = Country.from_dict(country_data) if country_data else None

        return cls(
            id=data.get('id'),
            country_id=data['country_id'],
            destination=data['destination'],
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            price=data['price'],
            image_url=data.get('image_url'),
            created_at=created_at,
            country=country
        )

    def __eq__(self, other: object) -> bool:
        """Compare two vacation objects."""
        if not isinstance(other, Vacation):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        """String representation of vacation."""
        return (
            f"Vacation(id={self.id}, destination={self.destination}, "
            f"dates={self.start_date} to {self.end_date}, price={self.price})"
        ) 