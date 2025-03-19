-- Create role enum type
CREATE TYPE role_enum AS ENUM ('admin', 'user');

-- Create countries table
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(2) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id role_enum NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vacations table
CREATE TABLE vacations (
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

-- Create likes table
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    vacation_id INTEGER NOT NULL REFERENCES vacations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, vacation_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_vacations_country_id ON vacations(country_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_vacation_id ON likes(vacation_id);

-- Insert some sample countries
INSERT INTO countries (name, code) VALUES
    ('United States', 'US'),
    ('United Kingdom', 'GB'),
    ('France', 'FR'),
    ('Italy', 'IT'),
    ('Spain', 'ES'),
    ('Japan', 'JP'),
    ('Australia', 'AU'),
    ('Canada', 'CA'),
    ('Germany', 'DE'),
    ('Brazil', 'BR');

-- Insert a default admin user (password should be hashed in production)
INSERT INTO users (first_name, last_name, email, password, role_id) VALUES
    ('Admin', 'User', 'admin@example.com', 'hashed_password_here', 'admin'); 