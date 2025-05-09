from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/users/*": {"origins": "http://142.93.145.102:4200"}})  # Enable CORS for all routes

# Ensure data and configs directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('configs', exist_ok=True)


@app.route('/app/status', methods=['GET'])
def status():
    return jsonify({"status": "server running"}), 200
@app.route('/users/set-up', methods=['POST'])
def setup_user():
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'description', 'group', 'publicKey']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data['username']
    
    # Check if user already exists
    users_file = 'data/users.txt'
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            existing_users = [line.strip() for line in f.readlines()]
            if username in existing_users:
                return jsonify({'error': 'User already exists'}), 400
    
    # Add user to users.txt
    with open(users_file, 'a') as f:
        f.write(f"{username}\n")
    
    # Create user config file
    current_date = datetime.now().strftime('%Y%m%d')
    config_filename = f"configs/{username}_{current_date}.txt"
    
    with open(config_filename, 'w') as f:
        f.write(f"{username}:{data['group']}:{data['description']}:{data['publicKey']}")
    
    return jsonify({'message': 'User setup completed successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050) 
