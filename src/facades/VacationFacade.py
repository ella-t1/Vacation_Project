"""
VacationFacade provides a high-level interface for managing vacations and their interactions.
This includes vacation CRUD operations and like/unlike functionality.
"""
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal

from src.models.Vacation import Vacation
from src.models.Like import Like
from src.DAL.VacationService import VacationService
from src.DAL.LikeService import LikeService
from src.DAL.CountryService import CountryService


class VacationFacade:
    def __init__(self):
        """Initialize the VacationFacade with required services."""
        self.vacation_service = VacationService()
        self.like_service = LikeService()
        self.country_service = CountryService()

    def _format_vacation_dict(self, vacation: Vacation) -> Dict:
        """
        Format a vacation object into a dictionary with proper date types.
        
        Args:
            vacation: Vacation object to format
            
        Returns:
            Dictionary with properly formatted fields
        """
        vacation_dict = vacation.to_dict()
        
        # Convert string dates to date objects if they're strings
        if isinstance(vacation_dict['start_date'], str):
            vacation_dict['start_date'] = datetime.strptime(
                vacation_dict['start_date'], '%Y-%m-%d'
            ).date()
            
        if isinstance(vacation_dict['end_date'], str):
            vacation_dict['end_date'] = datetime.strptime(
                vacation_dict['end_date'], '%Y-%m-%d'
            ).date()
            
        # Convert price to Decimal if it's a string
        if isinstance(vacation_dict['price'], str):
            vacation_dict['price'] = Decimal(vacation_dict['price'])
            
        return vacation_dict

    def create_vacation(self, country_code: str, destination: str, description: str,
                       start_date: date, end_date: date, price: Decimal,
                       image_url: Optional[str] = None) -> Dict:
        """
        Create a new vacation.

        Args:
            country_code: Two-letter country code
            destination: Name of the destination
            description: Description of the vacation
            start_date: Start date of the vacation
            end_date: End date of the vacation
            price: Price of the vacation
            image_url: Optional URL for vacation image

        Returns:
            Dictionary representation of the created vacation

        Raises:
            ValueError: If country code is invalid or dates are invalid
        """
        # Verify country exists
        country = self.country_service.get_by_code(country_code)
        if not country:
            raise ValueError(f"Invalid country code: {country_code}")

        # Validate dates
        if start_date >= end_date:
            raise ValueError("End date must be after start date")

        # Create vacation
        vacation = Vacation(
            country_id=country.id,
            destination=destination,
            description=description,
            start_date=start_date,
            end_date=end_date,
            price=price,
            image_url=image_url
        )
        
        created_vacation = self.vacation_service.create(vacation)
        return self._format_vacation_dict(created_vacation)

    def get_vacation(self, vacation_id: int, user_id: Optional[int] = None) -> Dict:
        """
        Get a vacation by ID, optionally including like status for a user.

        Args:
            vacation_id: ID of the vacation
            user_id: Optional user ID to check like status

        Returns:
            Dictionary with vacation details and like status if user_id provided

        Raises:
            ValueError: If vacation not found
        """
        vacation = self.vacation_service.get_by_id(vacation_id)
        if not vacation:
            raise ValueError(f"Vacation not found: {vacation_id}")

        result = self._format_vacation_dict(vacation)
        
        # Add like information if user_id provided
        if user_id:
            result['is_liked'] = self.like_service.has_user_liked(user_id, vacation_id)
            result['likes_count'] = self.like_service.count_by_vacation(vacation_id)

        return result

    def update_vacation(self, vacation_id: int, **kwargs) -> Dict:
        """
        Update a vacation's details.

        Args:
            vacation_id: ID of the vacation to update
            **kwargs: Fields to update (country_code, destination, description,
                     start_date, end_date, price, image_url)

        Returns:
            Updated vacation as dictionary

        Raises:
            ValueError: If vacation not found or update data invalid
        """
        # Get existing vacation
        vacation = self.vacation_service.get_by_id(vacation_id)
        if not vacation:
            raise ValueError(f"Vacation not found: {vacation_id}")

        # Handle country code update
        if 'country_code' in kwargs:
            country = self.country_service.get_by_code(kwargs['country_code'])
            if not country:
                raise ValueError(f"Invalid country code: {kwargs['country_code']}")
            kwargs['country_id'] = country.id
            del kwargs['country_code']

        # Validate dates if both are provided
        if 'start_date' in kwargs and 'end_date' in kwargs:
            if kwargs['start_date'] >= kwargs['end_date']:
                raise ValueError("End date must be after start date")
        elif 'start_date' in kwargs and kwargs['start_date'] >= vacation.end_date:
            raise ValueError("Start date must be before current end date")
        elif 'end_date' in kwargs and vacation.start_date >= kwargs['end_date']:
            raise ValueError("End date must be after current start date")

        # Update vacation
        for key, value in kwargs.items():
            setattr(vacation, key, value)

        updated_vacation = self.vacation_service.update(vacation)
        return self._format_vacation_dict(updated_vacation)

    def delete_vacation(self, vacation_id: int) -> bool:
        """
        Delete a vacation.

        Args:
            vacation_id: ID of the vacation to delete

        Returns:
            True if vacation was deleted

        Raises:
            ValueError: If vacation not found
        """
        if not self.vacation_service.get_by_id(vacation_id):
            raise ValueError(f"Vacation not found: {vacation_id}")

        return self.vacation_service.delete(vacation_id)

    def like_vacation(self, user_id: int, vacation_id: int) -> Dict:
        """
        Like a vacation for a user.

        Args:
            user_id: ID of the user
            vacation_id: ID of the vacation

        Returns:
            Dictionary with like details

        Raises:
            ValueError: If vacation not found or already liked
        """
        # Verify vacation exists
        if not self.vacation_service.get_by_id(vacation_id):
            raise ValueError(f"Vacation not found: {vacation_id}")

        # Check if already liked
        if self.like_service.has_user_liked(user_id, vacation_id):
            raise ValueError(f"User {user_id} has already liked vacation {vacation_id}")

        # Create like
        like = Like(user_id=user_id, vacation_id=vacation_id)
        created_like = self.like_service.create(like)
        
        return {
            'id': created_like.id,
            'user_id': created_like.user_id,
            'vacation_id': created_like.vacation_id,
            'created_at': created_like.created_at
        }

    def unlike_vacation(self, user_id: int, vacation_id: int) -> bool:
        """
        Remove a like from a vacation for a user.

        Args:
            user_id: ID of the user
            vacation_id: ID of the vacation

        Returns:
            True if like was removed

        Raises:
            ValueError: If vacation not found or not liked
        """
        # Verify vacation exists
        if not self.vacation_service.get_by_id(vacation_id):
            raise ValueError(f"Vacation not found: {vacation_id}")

        # Check if liked
        if not self.like_service.has_user_liked(user_id, vacation_id):
            raise ValueError(f"User {user_id} has not liked vacation {vacation_id}")

        # Delete like
        return self.like_service.delete(user_id, vacation_id)

    def get_user_liked_vacations(self, user_id: int) -> List[Dict]:
        """
        Get all vacations liked by a user.

        Args:
            user_id: ID of the user

        Returns:
            List of vacation dictionaries with like information
        """
        liked_vacations = self.like_service.get_by_user(user_id)
        result = []
        
        for vacation_data in liked_vacations:
            vacation = Vacation.from_dict(vacation_data)
            vacation_dict = self._format_vacation_dict(vacation)
            vacation_dict['is_liked'] = True
            vacation_dict['likes_count'] = self.like_service.count_by_vacation(vacation.id)
            result.append(vacation_dict)

        return result

    def get_popular_vacations(self, limit: int = 10) -> List[Dict]:
        """
        Get most liked vacations.

        Args:
            limit: Maximum number of vacations to return

        Returns:
            List of vacation dictionaries with like counts
        """
        popular_vacations = self.like_service.get_popular_vacations(limit)
        result = []
        
        for vacation_data in popular_vacations:
            vacation = Vacation.from_dict(vacation_data)
            vacation_dict = self._format_vacation_dict(vacation)
            vacation_dict['likes_count'] = vacation_data['like_count']
            result.append(vacation_dict)

        return result

    def search_vacations(self, query: Optional[str] = None, country_code: Optional[str] = None,
                        min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None,
                        start_date: Optional[date] = None, end_date: Optional[date] = None,
                        user_id: Optional[int] = None) -> List[Dict]:
        """
        Search for vacations with optional filters.

        Args:
            query: Optional search text for destination or description
            country_code: Optional country code to filter by
            min_price: Optional minimum price
            max_price: Optional maximum price
            start_date: Optional start date
            end_date: Optional end date
            user_id: Optional user ID to include like status

        Returns:
            List of vacation dictionaries matching the criteria
        """
        # Convert country code to ID if provided
        country_id = None
        if country_code:
            country = self.country_service.get_by_code(country_code)
            if not country:
                raise ValueError(f"Invalid country code: {country_code}")
            country_id = country.id

        # Get initial vacation list based on search term
        if query:
            vacations = self.vacation_service.search(query)
        else:
            vacations = self.vacation_service.get_all()

        # Apply filters
        filtered_vacations = []
        for vacation in vacations:
            # Apply country filter
            if country_id and vacation.country_id != country_id:
                continue

            # Apply price filters
            if min_price and vacation.price < min_price:
                continue
            if max_price and vacation.price > max_price:
                continue

            # Apply date filters
            if start_date and vacation.start_date < start_date:
                continue
            if end_date and vacation.end_date > end_date:
                continue

            filtered_vacations.append(vacation)

        # Format results and add like information
        result = []
        for vacation in filtered_vacations:
            vacation_dict = self._format_vacation_dict(vacation)
            if user_id:
                vacation_dict['is_liked'] = self.like_service.has_user_liked(user_id, vacation.id)
                vacation_dict['likes_count'] = self.like_service.count_by_vacation(vacation.id)
            result.append(vacation_dict)

        return result
