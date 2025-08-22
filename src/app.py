from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Get CORS allowed origins from environment variable with default
cors_origin = os.getenv("CORS_ORIGIN", "http://159.203.27.125/")
CORS(app, resources={r"/users/*": {"origins": cors_origin}})  # Enable CORS for all routes

# Ensure configs directory exists
os.makedirs('configs', exist_ok=True)

# Database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "159.203.27.125")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Initialize database table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create users table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            user_group VARCHAR(255),
            description TEXT,
            public_key TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

# Function to migrate existing users from text file to database
def migrate_existing_users():
    users_file = 'data/users.txt'
    if not os.path.exists(users_file):
        return

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        with open(users_file, 'r') as f:
            usernames = [line.strip() for line in f.readlines() if line.strip()]

        for username in usernames:
            # Check if user already exists in database
            cur.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                continue

            # Find the most recent config file for this user
            config_files = [f for f in os.listdir('configs') if f.startswith(f"{username}_")]
            if not config_files:
                continue

            # Sort by date (newest first)
            config_files.sort(reverse=True)
            latest_config = os.path.join('configs', config_files[0])

            try:
                with open(latest_config, 'r') as cf:
                    config_data = cf.read().strip().split(':')
                    if len(config_data) >= 4:
                        # Insert user into database
                        cur.execute(
                            "INSERT INTO users (username, user_group, description, public_key) VALUES (%s, %s, %s, %s)",
                            (username, config_data[1], config_data[2], config_data[3])
                        )
            except Exception as e:
                print(f"Error processing config for {username}: {e}")

        conn.commit()
    except Exception as e:
        print(f"Error migrating users: {e}")
    finally:
        cur.close()
        conn.close()

# Initialize the database on startup
init_db()

# Migrate existing users
migrate_existing_users()


@app.route('/app/status', methods=['GET'])
def status():
    return jsonify({"status": "server running with new changes"}), 200

@app.route('/users/update', methods=['PUT'])
def update_user():
    data = request.json

    # Validate required fields
    required_fields = ['username', 'description', 'group', 'publicKey']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']

    # Check if user exists in the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user_exists = cur.fetchone()

    if not user_exists:
        cur.close()
        conn.close()
        return jsonify({'error': 'User does not exist'}), 404

    # Update user in the database
    cur.execute(
        """
        UPDATE users 
        SET user_group = %s, description = %s, public_key = %s, update_date = CURRENT_TIMESTAMP
        WHERE username = %s
        """,
        (data['group'], data['description'], data['publicKey'], username)
    )

    conn.commit()
    cur.close()
    conn.close()

    # Update user config file (keeping this for backward compatibility)
    current_date = datetime.now().strftime('%Y%m%d')
    config_filename = f"configs/{username}_{current_date}.txt"

    with open(config_filename, 'w') as f:
        f.write(f"{username}:{data['group']}:{data['description']}:{data['publicKey']}")

    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/users/get/<username>', methods=['GET'])
def get_user(username):
    # Get user from the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, user_group, description, public_key, 
               created_date, update_date 
        FROM users 
        WHERE username = %s
    """, (username,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Format the response
    user_data = {
        'username': user[0],
        'group': user[1],
        'description': user[2],
        'publicKey': user[3],
        'createdDate': user[4].isoformat() if user[4] else None,
        'updateDate': user[5].isoformat() if user[5] else None
    }

    return jsonify(user_data), 200

@app.route('/users/list', methods=['GET'])
def list_users():
    # Get all users from the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, user_group, description, 
               created_date, update_date 
        FROM users 
        ORDER BY username
    """)

    users = cur.fetchall()
    cur.close()
    conn.close()

    # Format the response
    user_list = []
    for user in users:
        user_data = {
            'username': user[0],
            'group': user[1],
            'description': user[2],
            'createdDate': user[3].isoformat() if user[3] else None,
            'updateDate': user[4].isoformat() if user[4] else None
        }
        user_list.append(user_data)

    return jsonify(user_list), 200

@app.route('/users/set-up', methods=['POST'])
def setup_user():
    data = request.json

    # Validate required fields
    required_fields = ['username', 'description', 'group', 'publicKey']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']

    # Check if user already exists in the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user_exists = cur.fetchone()

    if user_exists:
        cur.close()
        conn.close()
        return jsonify({'error': 'User already exists'}), 400

    # Add user to the database
    cur.execute(
        "INSERT INTO users (username, user_group, description, public_key) VALUES (%s, %s, %s, %s)",
        (username, data['group'], data['description'], data['publicKey'])
    )

    conn.commit()
    cur.close()
    conn.close()

    # Create user config file (keeping this for backward compatibility)
    current_date = datetime.now().strftime('%Y%m%d')
    config_filename = f"configs/{username}_{current_date}.txt"

    with open(config_filename, 'w') as f:
        f.write(f"{username}:{data['group']}:{data['description']}:{data['publicKey']}")

    return jsonify({'message': 'User setup completed successfully'}), 201

if __name__ == '__main__':
    # Get host and port from environment variables with defaults
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8050"))
    app.run(host=host, port=port)
