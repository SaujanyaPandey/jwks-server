import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect("totally_not_my_privateKeys.db")
cursor = conn.cursor()

# Create the "keys" table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS keys(
    kid INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    exp INTEGER NOT NULL
)
""")

# Save and close
conn.commit()
conn.close()

print("Database and table created successfully!")
