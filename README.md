# User Management API

A Flask-based REST API for managing user configurations with SSH key storage.

## Features

- User registration with username, description, group, and SSH public key
- Duplicate username prevention
- Automatic configuration file generation
- CORS enabled for frontend integration

## API Endpoints

### POST /users/set-up
Creates a new user configuration.

**Request Body:**
```json
{
    "username": "string",
    "description": "string",
    "group": "string",
    "publicKey": "string"
}
```

**Responses:**
- 201: User created successfully
- 400: User already exists or missing required fields

### PUT /users/update
Updates an existing user configuration.

**Request Body:**
```json
{
    "username": "string",
    "description": "string",
    "group": "string",
    "publicKey": "string"
}
```

**Responses:**
- 200: User updated successfully
- 400: Missing required fields
- 404: User does not exist

### GET /users/get/{username}
Retrieves details for a specific user.

**Path Parameters:**
- username: The username of the user to retrieve

**Responses:**
- 200: User details retrieved successfully
- 404: User not found

### GET /users/list
Retrieves a list of all users.

**Responses:**
- 200: List of users retrieved successfully

## Data Storage

The application uses PostgreSQL for data storage with the following structure:

- `users` table: Stores user information with the following columns:
  - `username`: Primary key, unique identifier for each user
  - `user_group`: User's group/role
  - `description`: User description
  - `public_key`: User's SSH public key
  - `created_date`: Timestamp when the user was created
  - `update_date`: Timestamp when the user was last updated

For backward compatibility, the application also maintains:
- `configs/`: Directory containing user configuration files
  - Format: `username_YYYYMMDD.txt`
  - Content: `username:group:description:publicKey`

## Requirements

### Python Version
This application is compatible with Python 3.13.3 or higher. The requirements.txt file has been updated to ensure compatibility with Python 3.13.3.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
   - Create a database for the application
   - Set up environment variables for database connection (see [Environment Variables](#environment-variables) section)
   - Default configuration (if no environment variables are set):
     - Host: localhost
     - User: postgres
     - Password: root
     - Database: devops_user_table

   You can create the database using the following command:
   ```bash
   createdb -U postgres devops_user_table
   ```

4. Run the application:
```bash
python src/app.py
```

The API will be available at `http://localhost:8050`

Note: The application will automatically create the necessary tables in the database when it starts.

## Dependencies

- Flask: Web framework
- Flask-CORS: Cross-Origin Resource Sharing support
- Python-dotenv: Environment variable management
- Requests: HTTP client library
- Pytest: Testing framework
- psycopg[binary]: PostgreSQL database adapter (for Python 3.13+)

## Database Setup

This application uses PostgreSQL for data storage. Make sure you have PostgreSQL installed and running before starting the application.

### PostgreSQL Installation

This application uses the appropriate PostgreSQL adapter based on your Python version:

- For Python 3.13+: `psycopg[binary]` (psycopg 3)
- For Python 3.11 or lower: `psycopg2-binary==2.9.7`

### Environment Variables

The application now uses environment variables for database configuration, which allows for easier deployment across different environments (development, staging, production) without modifying the code.

#### Setting Up Environment Variables

1. Copy the `.env.example` file to a new file named `.env`:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```
# Database Configuration
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password

# Application Configuration
APP_HOST=your_app_host
APP_PORT=your_app_port
CORS_ORIGIN=your_cors_allowed_origin
```

3. For different environments, you can create different .env files:
   - `.env.development`
   - `.env.staging`
   - `.env.production`

   And load the appropriate one based on your environment:
   ```python
   # In app.py
   from dotenv import load_dotenv
   import os

   # Load environment variables based on environment
   env = os.getenv("FLASK_ENV", "development")
   load_dotenv(f".env.{env}")
   ```

Note: The `.env` file is excluded from version control in `.gitignore` to prevent sensitive information from being committed to the repository.
