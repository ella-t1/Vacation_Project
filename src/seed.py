from datetime import datetime, timedelta
from src.dal.query import query, hash_password

def get_sample_users():
    """Return sample user data."""
    return [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': hash_password('password123'),
            'role_id': 'user'
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'password': hash_password('password123'),
            'role_id': 'user'
        }
    ]

def get_sample_vacations():
    """Return sample vacation data."""
    return [
        {
            'country_id': 1,  # United States
            'destination': 'Hawaii Paradise',
            'description': 'Experience the magic of Hawaii with this all-inclusive package. Visit stunning beaches, explore volcanic landscapes, and immerse yourself in rich Polynesian culture.',
            'start_date': datetime.now() + timedelta(days=30),
            'end_date': datetime.now() + timedelta(days=37),
            'price': 2999.99,
            'image_url': 'assets/images/hawaii.jpg'
        },
        {
            'country_id': 2,  # United Kingdom
            'destination': 'London Explorer',
            'description': 'Discover the historic charm of London. Visit Buckingham Palace, Tower Bridge, and the British Museum. Includes guided tours and luxury accommodation.',
            'start_date': datetime.now() + timedelta(days=45),
            'end_date': datetime.now() + timedelta(days=52),
            'price': 2499.99,
            'image_url': 'assets/images/london.jpg'
        },
        {
            'country_id': 3,  # France
            'destination': 'Paris Romance',
            'description': 'Experience the romance of Paris. Visit the Eiffel Tower, Louvre Museum, and Notre-Dame. Includes Seine River cruise and fine dining experiences.',
            'start_date': datetime.now() + timedelta(days=60),
            'end_date': datetime.now() + timedelta(days=67),
            'price': 2799.99,
            'image_url': 'assets/images/paris.jpg'
        },
        {
            'country_id': 4,  # Italy
            'destination': 'Rome & Florence',
            'description': 'Explore the art and history of Italy. Visit the Colosseum, Vatican City, and Florence\'s Renaissance treasures. Includes wine tasting and cooking classes.',
            'start_date': datetime.now() + timedelta(days=75),
            'end_date': datetime.now() + timedelta(days=82),
            'price': 3199.99,
            'image_url': 'assets/images/italy.jpg'
        },
        {
            'country_id': 5,  # Spain
            'destination': 'Barcelona Adventure',
            'description': 'Discover the vibrant city of Barcelona. Visit Gaudi\'s masterpieces, enjoy tapas tours, and relax on Mediterranean beaches. Includes flamenco show.',
            'start_date': datetime.now() + timedelta(days=90),
            'end_date': datetime.now() + timedelta(days=97),
            'price': 2299.99,
            'image_url': 'assets/images/barcelona.jpg'
        }
    ]

def seed_users(users):
    """Seed users into the database."""
    print("Starting to seed users...")
    for user in users:
        query("""
            INSERT INTO users (first_name, last_name, email, password, role_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (user['first_name'], user['last_name'], user['email'],
              user['password'], user['role_id']), fetch=False)
    print("Users seeded successfully!")

def seed_vacations(vacations):
    """Seed vacations into the database."""
    print("Starting to seed vacations...")
    for vacation in vacations:
        query("""
            INSERT INTO vacations (country_id, destination, description,
                                 start_date, end_date, price, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (vacation['country_id'], vacation['destination'],
              vacation['description'], vacation['start_date'],
              vacation['end_date'], vacation['price'],
              vacation['image_url']), fetch=False)
    print("Vacations seeded successfully!")

def seed_database():
    """Seed the database with sample data."""
    try:
        users = get_sample_users()
        vacations = get_sample_vacations()
        
        seed_users(users)
        seed_vacations(vacations)
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise

if __name__ == "__main__":
    print("Starting database seeding process...")
    seed_database() 