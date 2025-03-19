from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
from src.query import query
from src.models.Vacation import Vacation
from src.models.Country import Country

class VacationService:
    @staticmethod
    def create(vacation: Vacation) -> Vacation:
        """
        Create a new vacation.
        
        Args:
            vacation: Vacation object to create
            
        Returns:
            Created vacation with ID
            
        Raises:
            ValueError: If country doesn't exist
        """
        # Verify country exists
        check_sql = "SELECT EXISTS(SELECT 1 FROM countries WHERE id = %s)"
        check_result = query(check_sql, [vacation.country_id])
        if not check_result[0]['exists']:
            raise ValueError(f"Country with id {vacation.country_id} not found")

        sql = """
            WITH inserted AS (
                INSERT INTO vacations (
                    country_id, destination, description,
                    start_date, end_date, price, image_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            )
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at
            FROM inserted v
            JOIN countries c ON v.country_id = c.id
        """
        params = [
            vacation.country_id,
            vacation.destination,
            vacation.description,
            vacation.start_date,
            vacation.end_date,
            vacation.price,
            vacation.image_url
        ]
        result = query(sql, params, commit=True)
        return VacationService._load_with_country(result[0])

    @staticmethod
    def get_by_id(vacation_id: int) -> Optional[Vacation]:
        """
        Get vacation by ID.
        
        Args:
            vacation_id: Vacation ID
            
        Returns:
            Vacation object if found, None otherwise
        """
        sql = """
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at
            FROM vacations v
            JOIN countries c ON v.country_id = c.id
            WHERE v.id = %s
        """
        result = query(sql, [vacation_id])
        return VacationService._load_with_country(result[0]) if result else None

    @staticmethod
    def update(vacation: Vacation) -> Vacation:
        """
        Update vacation information.
        
        Args:
            vacation: Vacation object with updated information
            
        Returns:
            Updated vacation object
            
        Raises:
            ValueError: If vacation doesn't exist or country doesn't exist
        """
        if not VacationService.get_by_id(vacation.id):
            raise ValueError(f"Vacation with id {vacation.id} not found")

        # Verify country exists
        check_sql = "SELECT EXISTS(SELECT 1 FROM countries WHERE id = %s)"
        check_result = query(check_sql, [vacation.country_id])
        if not check_result[0]['exists']:
            raise ValueError(f"Country with id {vacation.country_id} not found")

        sql = """
            WITH updated AS (
                UPDATE vacations 
                SET country_id = %s,
                    destination = %s,
                    description = %s,
                    start_date = %s,
                    end_date = %s,
                    price = %s,
                    image_url = %s
                WHERE id = %s
                RETURNING *
            )
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at
            FROM updated v
            JOIN countries c ON v.country_id = c.id
        """
        params = [
            vacation.country_id,
            vacation.destination,
            vacation.description,
            vacation.start_date,
            vacation.end_date,
            vacation.price,
            vacation.image_url,
            vacation.id
        ]
        result = query(sql, params, commit=True)
        return VacationService._load_with_country(result[0])

    @staticmethod
    def delete(vacation_id: int) -> bool:
        """
        Delete a vacation.
        
        Args:
            vacation_id: ID of vacation to delete
            
        Returns:
            True if vacation was deleted
            
        Raises:
            ValueError: If vacation has associated likes
        """
        # Check for associated likes
        check_sql = "SELECT EXISTS(SELECT 1 FROM likes WHERE vacation_id = %s)"
        check_result = query(check_sql, [vacation_id])
        if check_result[0]['exists']:
            raise ValueError("Cannot delete vacation with associated likes")

        sql = "DELETE FROM vacations WHERE id = %s"
        query(sql, [vacation_id], commit=True)
        return True

    @staticmethod
    def get_all(
        country_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = 'start_date',
        sort_order: str = 'asc'
    ) -> List[Vacation]:
        """
        Get all vacations with optional filtering.
        
        Args:
            country_id: Filter by country ID
            min_price: Filter by minimum price
            max_price: Filter by maximum price
            start_date: Filter by start date
            end_date: Filter by end date
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            List of vacations matching criteria
        """
        sql = """
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at
            FROM vacations v
            JOIN countries c ON v.country_id = c.id
            WHERE 1=1
        """
        params = []

        if country_id:
            sql += " AND v.country_id = %s"
            params.append(country_id)

        if min_price:
            sql += " AND v.price >= %s"
            params.append(min_price)

        if max_price:
            sql += " AND v.price <= %s"
            params.append(max_price)

        if start_date:
            sql += " AND v.start_date >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND v.end_date <= %s"
            params.append(end_date)

        # Validate and apply sorting
        valid_sort_fields = {'start_date', 'end_date', 'price', 'destination'}
        valid_sort_orders = {'asc', 'desc'}
        
        if sort_by not in valid_sort_fields:
            sort_by = 'start_date'
        if sort_order.lower() not in valid_sort_orders:
            sort_order = 'asc'

        sql += f" ORDER BY v.{sort_by} {sort_order}"
        
        result = query(sql, params)
        return [VacationService._load_with_country(row) for row in result]

    @staticmethod
    def search(term: str) -> List[Vacation]:
        """
        Search vacations by destination or description.
        
        Args:
            term: Search term
            
        Returns:
            List of matching vacations
        """
        sql = """
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at
            FROM vacations v
            JOIN countries c ON v.country_id = c.id
            WHERE v.destination ILIKE %s 
                OR v.description ILIKE %s
            ORDER BY v.start_date
        """
        pattern = f"%{term}%"
        result = query(sql, [pattern, pattern])
        return [VacationService._load_with_country(row) for row in result]

    @staticmethod
    def count(country_id: Optional[int] = None) -> int:
        """
        Get total number of vacations.
        
        Args:
            country_id: Optional country ID to filter by
            
        Returns:
            Total number of vacations
        """
        sql = "SELECT COUNT(*) as count FROM vacations"
        params = []
        
        if country_id:
            sql += " WHERE country_id = %s"
            params.append(country_id)
            
        result = query(sql, params)
        return result[0]['count']

    @staticmethod
    def _load_with_country(row: Dict) -> Vacation:
        """
        Create a Vacation instance from a database row, including country data.
        
        Args:
            row: Database row with vacation and country data
            
        Returns:
            Vacation instance with associated Country
        """
        # Extract country data
        country = Country(
            id=row['c_id'],
            name=row['c_name'],
            code=row['c_code'],
            created_at=row['c_created_at']
        )
        
        # Create vacation data dictionary
        vacation_data = {
            'id': row['id'],
            'country_id': row['country_id'],
            'destination': row['destination'],
            'description': row['description'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'price': row['price'],
            'image_url': row['image_url'],
            'created_at': row['created_at'],
            'country': country.to_dict()
        }
        
        return Vacation.from_dict(vacation_data) 