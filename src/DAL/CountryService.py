from typing import List, Optional
from src.query import query
from src.models.Country import Country

class CountryService:
    @staticmethod
    def create(country: Country) -> Country:
        """
        Create a new country.
        
        Args:
            country: Country object to create
            
        Returns:
            Created country with ID
            
        Raises:
            ValueError: If country with same code already exists
        """
        if CountryService.get_by_code(country.code):
            raise ValueError(f"Country with code {country.code} already exists")

        sql = """
            INSERT INTO countries (name, code)
            VALUES (%s, %s)
            RETURNING *
        """
        params = [country.name, country.code]
        result = query(sql, params, commit=True)
        return Country.from_dict(result[0])

    @staticmethod
    def get_by_id(country_id: int) -> Optional[Country]:
        """
        Get country by ID.
        
        Args:
            country_id: Country ID
            
        Returns:
            Country object if found, None otherwise
        """
        sql = "SELECT * FROM countries WHERE id = %s"
        result = query(sql, [country_id])
        return Country.from_dict(result[0]) if result else None

    @staticmethod
    def get_by_code(code: str) -> Optional[Country]:
        """
        Get country by code.
        
        Args:
            code: Two-letter ISO country code
            
        Returns:
            Country object if found, None otherwise
        """
        sql = "SELECT * FROM countries WHERE code = %s"
        result = query(sql, [code.upper()])
        return Country.from_dict(result[0]) if result else None

    @staticmethod
    def update(country: Country) -> Country:
        """
        Update country information.
        
        Args:
            country: Country object with updated information
            
        Returns:
            Updated country object
            
        Raises:
            ValueError: If country doesn't exist or code is already in use
        """
        if not CountryService.get_by_id(country.id):
            raise ValueError(f"Country with id {country.id} not found")

        existing = CountryService.get_by_code(country.code)
        if existing and existing.id != country.id:
            raise ValueError(f"Country code {country.code} is already in use")

        sql = """
            UPDATE countries 
            SET name = %s, code = %s
            WHERE id = %s
            RETURNING *
        """
        params = [country.name, country.code, country.id]
        result = query(sql, params, commit=True)
        return Country.from_dict(result[0])

    @staticmethod
    def delete(country_id: int) -> bool:
        """
        Delete a country.
        
        Args:
            country_id: ID of country to delete
            
        Returns:
            True if country was deleted, False otherwise
            
        Raises:
            ValueError: If country has associated vacations
        """
        # Check for associated vacations
        check_sql = "SELECT EXISTS(SELECT 1 FROM vacations WHERE country_id = %s)"
        check_result = query(check_sql, [country_id])
        if check_result[0]['exists']:
            raise ValueError("Cannot delete country with associated vacations")

        sql = "DELETE FROM countries WHERE id = %s"
        query(sql, [country_id], commit=True)
        return True

    @staticmethod
    def get_all() -> List[Country]:
        """
        Get all countries.
        
        Returns:
            List of all countries, sorted by name
        """
        sql = "SELECT * FROM countries ORDER BY name"
        result = query(sql)
        return [Country.from_dict(row) for row in result]

    @staticmethod
    def search(term: str) -> List[Country]:
        """
        Search countries by name or code.
        
        Args:
            term: Search term
            
        Returns:
            List of matching countries
        """
        sql = """
            SELECT * FROM countries 
            WHERE name ILIKE %s OR code ILIKE %s 
            ORDER BY name
        """
        pattern = f"%{term}%"
        result = query(sql, [pattern, pattern])
        return [Country.from_dict(row) for row in result]

    @staticmethod
    def count() -> int:
        """
        Get total number of countries.
        
        Returns:
            Total number of countries
        """
        sql = "SELECT COUNT(*) as count FROM countries"
        result = query(sql)
        return result[0]['count'] 