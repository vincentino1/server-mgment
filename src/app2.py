# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
from datetime import datetime
import os

# this is a comment
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Celery configuration
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',  # or another message broker
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    djkeshfeif
)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

@app.route('/v2/users/set-up', methods=['POST'])
def setup_user():
    data = request.json
    required_fields = ['username', 'description', 'group', 'publicKey']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data['username']
    users_file = 'data/users.txt'
    
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            existing_users = [line.strip() for line in f.readlines()]
            if username in existing_users:
                return jsonify({'error': 'User already exists'}), 400
    
    # Register user by appending to file (if needed)
    with open(users_file, 'a') as f:
        f.write(f"{username}\n")
    
    # Optionally, create a configuration file if you want a persistent record
    current_date = datetime.now().strftime('%Y%m%d')
    config_filename = f"configs/{username}_{current_date}.txt"
    with open(config_filename, 'w') as f:
        f.write(f"{username}:{data['group']}:{data['description']}:{data['publicKey']}")
    
    # Trigger the background task with a short delay if needed
    create_user_account.apply_async(
        args=[data['username'], data['group'], data['description'], data['publicKey']],
        countdown=300  # 5-minute delay; remove or adjust if immediate processing is ok
    )
    
    return jsonify({'message': 'User setup initiated successfully'}), 201

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    app.run(host='0.0.0.0', port=8050)
