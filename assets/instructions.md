# Vacation Project Specifications

## Project Overview
A vacation management system that allows users to browse, like, and manage vacation destinations.

## Core Features

## Roles
### Admin
- Can add new vacations
- Can edit existing vacations
- Can delete vacations
- Can view all users
- Can view all likes

### User
- Can browse vacations
- Can like/unlike vacations
- Can view vacation details
- Can view their own likes

## Technical Requirements
### Database
- PostgreSQL database
- Connection string format: postgresql://username:password@localhost:5432/database_name

### Programming Language
- Python 3.x

## Virtual Environment
### Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Required Packages
- psycopg2-binary
- python-dotenv
- bcrypt
