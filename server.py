from flask import Flask, request, jsonify
import jwt
import sqlite3
import time

app = Flask(__name__)

def get_private_key(expired=False):
    conn = sqlite3.connect("totally_not_my_privateKeys.db")
    cursor = conn.cursor()

    if expired:
        cursor.execute("SELECT key FROM keys WHERE exp < strftime('%s','now') LIMIT 1")
    else:
        cursor.execute("SELECT key FROM keys WHERE exp > strftime('%s','now') LIMIT 1")

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None

@app.route("/auth", methods=["POST"])
def authenticate():
    expired = request.args.get("expired")
    private_key = get_private_key(expired=bool(expired))

    if not private_key:
        return jsonify
if __name__ == "__main__":
    print("Starting the server...")  # Add this line to confirm server starts
    app.run(port=8080)
