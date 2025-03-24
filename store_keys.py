import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import time

# Function to generate an RSA key
def generate_rsa_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    return private_key

# Function to save key to the database
def save_key_to_db(private_key, exp_time):
    # Convert key to PEM format (string)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')  # Convert bytes to string for storage

    # Connect to the database
    conn = sqlite3.connect("totally_not_my_privateKeys.db")
    cursor = conn.cursor()

    # Insert the key into the table
    cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", (pem, exp_time))

    # Save and close
    conn.commit()
    conn.close()
    print("Key saved successfully!")

# Generate two keys: one expired, one valid
expired_time = int(time.time()) - 10  # Expired 10 seconds ago
valid_time = int(time.time()) + 3600  # Expires in 1 hour

save_key_to_db(generate_rsa_key(), expired_time)
save_key_to_db(generate_rsa_key(), valid_time)
