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

## File Structure

- `data/users.txt`: Stores list of registered usernames (one per line)
- `configs/`: Directory containing user configuration files
  - Format: `username_YYYYMMDD.txt`
  - Content: `username:group:description:publicKey`

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

3. Run the application:
```bash
python src/app.py
```

The API will be available at `http://localhost:8050`

## Dependencies

- Flask: Web framework
- Flask-CORS: Cross-Origin Resource Sharing support
- Python-dotenv: Environment variable management
- Requests: HTTP client library
- Pytest: Testing framework 