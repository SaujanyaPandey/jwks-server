import os
import sqlite3
import base64
import uuid

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from passlib.hash import argon2

# Read AES Key from Environment
key = os.getenv("NOT_MY_KEY")
if not key:
    raise Exception("Environment variable NOT_MY_KEY not set")
key = key.encode()

# Initialize Flask app
app = Flask(__name__)

# Setup Rate Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per second"]
)

# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_ip TEXT NOT NULL,
            request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Encryption Functions
def encrypt(data):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode()

def decrypt(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    encrypted = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return (decryptor.update(encrypted) + decryptor.finalize()).decode()

# Log Authentication Requests
def log_auth_request(user_id, request_ip):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO auth_logs (request_ip, user_id) VALUES (?, ?)", (request_ip, user_id))
    conn.commit()
    conn.close()

# /register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    password = str(uuid.uuid4())
    password_hash = argon2.hash(password)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    finally:
        conn.close()

    return jsonify({"password": password}), 201

# /auth Endpoint (Example for logging auths)
@app.route('/auth', methods=['POST'])
@limiter.limit("10/second")  # Rate limit here
def auth():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and argon2.verify(password, user[1]):
        log_auth_request(user[0], request.remote_addr)
        return jsonify({"message": "Authentication successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Health Check Endpoint (optional)
@app.route('/')
def home():
    return "JWKS Server Running!"

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
