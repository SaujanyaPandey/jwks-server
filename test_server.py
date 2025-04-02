import sqlite3
import pytest
from server import app, init_db
import time
import jwt
from cryptography.hazmat.primitives import serialization

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ✅ Ensure database starts fresh for testing
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    conn = sqlite3.connect("totally_not_my_privateKeys.db")
    cursor = conn.cursor()

    # ✅ Add a valid key and an expired key
    private_key = serialization.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    pem_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", (pem_key, int(time.time()) + 3600))
    cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", (pem_key, int(time.time()) - 10))

    conn.commit()
    conn.close()

# ✅ Test: Fetching a valid JWT
def test_auth_valid_key(client):
    response = client.post("/auth")
    assert response.status_code == 200
    assert "token" in response.json

    # ✅ Ensure JWT is valid
    token = response.json["token"]
    assert token is not None

# ✅ Test: Fetching an expired JWT
def test_auth_expired_key(client):
    response = client.post("/auth?expired=true")
    assert response.status_code == 200
    assert "token" in response.json

# ✅ Test: No keys in the database
def test_no_keys_in_db(client):
    conn = sqlite3.connect("totally_not_my_privateKeys.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keys")  # Remove all keys
    conn.commit()
    conn.close()

    response = client.post("/auth")
    assert response.status_code == 400  # Should return an error

# ✅ Test: JWKS Endpoint
def test_jwks(client):
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    assert "keys" in response.json
    assert len(response.json["keys"]) > 0  # Ensure keys are present

# ✅ Test: Home Route
def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "JWKS Server is running"
