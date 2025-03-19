import pytest
from datetime import datetime
from src.models.User import User
from src.DAL.UserService import UserService
from src.config import get_test_config
from src.query import init_pool, close_pool, query

@pytest.fixture(scope="module")
def setup_db():
    """Initialize database connection for tests."""
    config, _ = get_test_config()  # Unpack tuple, ignore connection string
    init_pool(config)
    
    # Drop existing schema
    cleanup_sql = """
        DROP TYPE IF EXISTS role_enum CASCADE;
        DROP TABLE IF EXISTS likes CASCADE;
        DROP TABLE IF EXISTS vacations CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS countries CASCADE;
    """
    query(cleanup_sql, commit=True)
    
    # Initialize schema
    with open('SQL/schema.sql', 'r') as f:
        schema_sql = f.read()
        query(schema_sql, commit=True)
    
    yield
    close_pool()

@pytest.fixture(autouse=True)
def cleanup_users():
    """Clean up users table after each test."""
    yield
    # Delete all users except the admin user
    query = "DELETE FROM users WHERE email != 'admin@example.com'"
    UserService._execute_query(query)

def test_create_user(setup_db):
    """Test creating a new user."""
    user = User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="password123"
    )
    saved_user = UserService.create(user)
    
    assert saved_user.id is not None
    assert saved_user.first_name == "John"
    assert saved_user.last_name == "Doe"
    assert saved_user.email == "john@example.com"
    assert saved_user.role_id == "user"
    assert isinstance(saved_user.created_at, datetime)

def test_create_user_with_existing_email(setup_db):
    """Test creating a user with an existing email should fail."""
    user1 = User(
        first_name="John",
        last_name="Doe",
        email="duplicate@example.com",
        password="password123"
    )
    UserService.create(user1)

    user2 = User(
        first_name="Jane",
        last_name="Doe",
        email="duplicate@example.com",
        password="password456"
    )
    with pytest.raises(Exception):  # Should raise a unique constraint violation
        UserService.create(user2)

def test_get_by_id(setup_db):
    """Test retrieving a user by ID."""
    original_user = User(
        first_name="Get",
        last_name="ById",
        email="get.by.id@example.com",
        password="password123"
    )
    created_user = UserService.create(original_user)
    
    retrieved_user = UserService.get_by_id(created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email

def test_get_by_id_not_found(setup_db):
    """Test retrieving a non-existent user by ID."""
    non_existent_id = 99999
    user = UserService.get_by_id(non_existent_id)
    assert user is None

def test_get_by_email(setup_db):
    """Test retrieving a user by email."""
    email = "get.by.email@example.com"
    original_user = User(
        first_name="Get",
        last_name="ByEmail",
        email=email,
        password="password123"
    )
    UserService.create(original_user)
    
    retrieved_user = UserService.get_by_email(email)
    assert retrieved_user is not None
    assert retrieved_user.email == email

def test_get_by_email_not_found(setup_db):
    """Test retrieving a non-existent user by email."""
    non_existent_email = "nonexistent@example.com"
    user = UserService.get_by_email(non_existent_email)
    assert user is None

def test_update_user(setup_db):
    """Test updating a user's information."""
    user = User(
        first_name="Original",
        last_name="Name",
        email="original@example.com",
        password="password123"
    )
    created_user = UserService.create(user)
    
    created_user.first_name = "Updated"
    created_user.last_name = "UserName"
    updated_user = UserService.update(created_user)
    
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "UserName"
    assert updated_user.email == created_user.email
    assert updated_user.id == created_user.id

def test_update_nonexistent_user(setup_db):
    """Test updating a non-existent user."""
    user = User(
        id=99999,
        first_name="NonExistent",
        last_name="User",
        email="nonexistent@example.com"
    )
    with pytest.raises(ValueError):
        UserService.update(user)

def test_delete_user(setup_db):
    """Test deleting a user."""
    user = User(
        first_name="Delete",
        last_name="Me",
        email="delete.me@example.com",
        password="password123"
    )
    created_user = UserService.create(user)
    
    assert UserService.delete(created_user.id) is True
    assert UserService.get_by_id(created_user.id) is None

def test_delete_nonexistent_user(setup_db):
    """Test deleting a non-existent user."""
    non_existent_id = 99999
    assert UserService.delete(non_existent_id) is True  # Should return True even if user doesn't exist

def test_update_password(setup_db):
    """Test updating a user's password."""
    user = User(
        first_name="Password",
        last_name="Update",
        email="password.update@example.com",
        password="oldpassword"
    )
    created_user = UserService.create(user)
    
    new_password = "newpassword123"
    assert UserService.update_password(created_user.id, new_password) is True
    
    updated_user = UserService.get_by_id(created_user.id)
    assert updated_user.verify_password(new_password) is True

def test_exists(setup_db):
    """Test checking if a user exists by email."""
    email = "exists.test@example.com"
    user = User(
        first_name="Exists",
        last_name="Test",
        email=email,
        password="password123"
    )
    UserService.create(user)
    
    assert UserService.exists(email) is True
    assert UserService.exists("nonexistent@example.com") is False

def test_count(setup_db):
    """Test counting total number of users."""
    initial_count = UserService.count()
    
    # Create some test users
    users = [
        User(first_name=f"Count{i}", 
             last_name="Test", 
             email=f"count{i}@example.com",
             password="password123")
        for i in range(3)
    ]
    for user in users:
        UserService.create(user)
    
    final_count = UserService.count()
    assert final_count == initial_count + 3

def test_get_all(setup_db):
    """Test retrieving all users."""
    # Create some test users
    test_users = [
        User(first_name=f"GetAll{i}", 
             last_name="Test", 
             email=f"getall{i}@example.com",
             password="password123")
        for i in range(3)
    ]
    for user in test_users:
        UserService.create(user)
    
    all_users = UserService.get_all()
    assert len(all_users) >= 3  # There might be other users in the database
    
    # Verify that our test users are in the results
    test_emails = {f"getall{i}@example.com" for i in range(3)}
    result_emails = {user.email for user in all_users}
    assert test_emails.issubset(result_emails) 