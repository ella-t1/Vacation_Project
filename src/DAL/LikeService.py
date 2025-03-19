from typing import List, Optional, Dict
from src.query import query
from src.models.Like import Like
from src.models.User import User
from src.models.Vacation import Vacation


class LikeService:
    @staticmethod
    def create(like: Like) -> Like:
        """
        Create a new like.
        
        Args:
            like: Like object to create
            
        Returns:
            Created like with ID
            
        Raises:
            ValueError: If user or vacation doesn't exist, or if like already exists
        """
        # Verify user exists
        check_user_sql = "SELECT EXISTS(SELECT 1 FROM users WHERE id = %s)"
        check_user_result = query(check_user_sql, [like.user_id])
        if not check_user_result[0]['exists']:
            raise ValueError(f"User with id {like.user_id} not found")

        # Verify vacation exists
        check_vacation_sql = "SELECT EXISTS(SELECT 1 FROM vacations WHERE id = %s)"
        check_vacation_result = query(check_vacation_sql, [like.vacation_id])
        if not check_vacation_result[0]['exists']:
            raise ValueError(f"Vacation with id {like.vacation_id} not found")

        # Check if like already exists
        check_like_sql = """
            SELECT EXISTS(
                SELECT 1 FROM likes 
                WHERE user_id = %s AND vacation_id = %s
            )
        """
        check_like_result = query(check_like_sql, [like.user_id, like.vacation_id])
        if check_like_result[0]['exists']:
            raise ValueError("User has already liked this vacation")

        # Create like
        sql = """
            INSERT INTO likes (user_id, vacation_id)
            VALUES (%s, %s)
            RETURNING *
        """
        params = [like.user_id, like.vacation_id]
        result = query(sql, params, commit=True)
        return Like.from_dict(result[0])

    @staticmethod
    def delete(user_id: int, vacation_id: int) -> bool:
        """
        Delete a like.
        
        Args:
            user_id: ID of user who liked
            vacation_id: ID of vacation that was liked
            
        Returns:
            True if like was deleted, False if it didn't exist
        """
        sql = """
            DELETE FROM likes 
            WHERE user_id = %s AND vacation_id = %s
            RETURNING id
        """
        result = query(sql, [user_id, vacation_id], commit=True)
        return bool(result)

    @staticmethod
    def get_by_user(user_id: int) -> List[Dict]:
        """
        Get all vacations liked by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of vacations with like information
        """
        sql = """
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at,
                l.id as like_id,
                l.created_at as like_created_at
            FROM likes l
            JOIN vacations v ON l.vacation_id = v.id
            JOIN countries c ON v.country_id = c.id
            WHERE l.user_id = %s
            ORDER BY l.created_at DESC
        """
        result = query(sql, [user_id])
        return result

    @staticmethod
    def get_by_vacation(vacation_id: int) -> List[Dict]:
        """
        Get all users who liked a vacation.
        
        Args:
            vacation_id: Vacation ID
            
        Returns:
            List of users with like information
        """
        sql = """
            SELECT 
                u.*,
                l.id as like_id,
                l.created_at as like_created_at
            FROM likes l
            JOIN users u ON l.user_id = u.id
            WHERE l.vacation_id = %s
            ORDER BY l.created_at DESC
        """
        result = query(sql, [vacation_id])
        return result

    @staticmethod
    def count_by_vacation(vacation_id: int) -> int:
        """
        Get total number of likes for a vacation.
        
        Args:
            vacation_id: Vacation ID
            
        Returns:
            Number of likes
        """
        sql = "SELECT COUNT(*) as count FROM likes WHERE vacation_id = %s"
        result = query(sql, [vacation_id])
        return result[0]['count']

    @staticmethod
    def has_user_liked(user_id: int, vacation_id: int) -> bool:
        """
        Check if a user has liked a vacation.
        
        Args:
            user_id: User ID
            vacation_id: Vacation ID
            
        Returns:
            True if user has liked the vacation
        """
        sql = """
            SELECT EXISTS(
                SELECT 1 FROM likes 
                WHERE user_id = %s AND vacation_id = %s
            ) as exists
        """
        result = query(sql, [user_id, vacation_id])
        return result[0]['exists']

    @staticmethod
    def get_popular_vacations(limit: int = 10) -> List[Dict]:
        """
        Get most liked vacations.
        
        Args:
            limit: Maximum number of vacations to return
            
        Returns:
            List of vacations with like counts
        """
        sql = """
            SELECT 
                v.*,
                c.id as c_id,
                c.name as c_name,
                c.code as c_code,
                c.created_at as c_created_at,
                COUNT(l.id) as like_count
            FROM vacations v
            JOIN countries c ON v.country_id = c.id
            LEFT JOIN likes l ON v.id = l.vacation_id
            GROUP BY v.id, c.id
            ORDER BY like_count DESC
            LIMIT %s
        """
        return query(sql, [limit]) 