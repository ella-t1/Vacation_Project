-- Create role enum type if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role_enum') THEN
        CREATE TYPE role_enum AS ENUM ('admin', 'user');
    END IF;
END $$;

-- Create countries table if it doesn't exist
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(2) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id role_enum NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vacations table if it doesn't exist
CREATE TABLE IF NOT EXISTS vacations (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES countries(id),
    destination VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create likes table if it doesn't exist
CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    vacation_id INTEGER NOT NULL REFERENCES vacations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, vacation_id)
);

-- Create indexes if they don't exist
DO $$ 
BEGIN
    -- Create index for vacations.country_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'vacations' AND indexname = 'idx_vacations_country_id'
    ) THEN
        CREATE INDEX idx_vacations_country_id ON vacations(country_id);
    END IF;

    -- Create index for likes.user_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'likes' AND indexname = 'idx_likes_user_id'
    ) THEN
        CREATE INDEX idx_likes_user_id ON likes(user_id);
    END IF;

    -- Create index for likes.vacation_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'likes' AND indexname = 'idx_likes_vacation_id'
    ) THEN
        CREATE INDEX idx_likes_vacation_id ON likes(vacation_id);
    END IF;
END $$;

-- Insert sample data in correct order
DO $$
DECLARE
    us_id INTEGER;
    uk_id INTEGER;
    fr_id INTEGER;
    admin_id INTEGER;
    nyc_id INTEGER;
    london_id INTEGER;
    paris_id INTEGER;
BEGIN
    -- Insert countries if they don't exist and get their IDs
    INSERT INTO countries (name, code)
    VALUES ('United States', 'US')
    ON CONFLICT (code) DO UPDATE SET code = EXCLUDED.code
    RETURNING id INTO us_id;

    INSERT INTO countries (name, code)
    VALUES ('United Kingdom', 'GB')
    ON CONFLICT (code) DO UPDATE SET code = EXCLUDED.code
    RETURNING id INTO uk_id;

    INSERT INTO countries (name, code)
    VALUES ('France', 'FR')
    ON CONFLICT (code) DO UPDATE SET code = EXCLUDED.code
    RETURNING id INTO fr_id;

    -- Insert remaining countries
    INSERT INTO countries (name, code)
    VALUES
        ('Italy', 'IT'),
        ('Spain', 'ES'),
        ('Japan', 'JP'),
        ('Australia', 'AU'),
        ('Canada', 'CA'),
        ('Germany', 'DE'),
        ('Brazil', 'BR')
    ON CONFLICT (code) DO NOTHING;

    -- Insert admin user if doesn't exist and get ID
    INSERT INTO users (first_name, last_name, email, password, role_id)
    VALUES ('Admin', 'User', 'admin@example.com', 'hashed_password_here', 'admin')
    ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
    RETURNING id INTO admin_id;

    -- Insert sample vacations
    INSERT INTO vacations (country_id, destination, description, start_date, end_date, price)
    VALUES (us_id, 'New York City', 'Experience the Big Apple', '2024-06-01', '2024-06-07', 1500.00)
    ON CONFLICT DO NOTHING
    RETURNING id INTO nyc_id;

    INSERT INTO vacations (country_id, destination, description, start_date, end_date, price)
    VALUES (uk_id, 'London', 'Visit the historic capital', '2024-07-01', '2024-07-07', 1800.00)
    ON CONFLICT DO NOTHING
    RETURNING id INTO london_id;

    INSERT INTO vacations (country_id, destination, description, start_date, end_date, price)
    VALUES (fr_id, 'Paris', 'City of Love', '2024-08-01', '2024-08-07', 1700.00)
    ON CONFLICT DO NOTHING
    RETURNING id INTO paris_id;

    -- Insert sample likes (admin likes all destinations)
    INSERT INTO likes (user_id, vacation_id)
    VALUES 
        (admin_id, nyc_id),
        (admin_id, london_id),
        (admin_id, paris_id)
    ON CONFLICT DO NOTHING;
END $$; 