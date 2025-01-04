import sqlite3
from werkzeug.security import generate_password_hash

# Connect to SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Example user data
name = "John Doe"
email = "john@example.com"
password = "password123"
age = 25  # Example age

# Hash the password
password_hash = generate_password_hash(password)

# Insert user into the database
cursor.execute(
    "INSERT INTO users (name, email, password_hash, age) VALUES (?, ?, ?, ?)", 
    (name, email, password_hash, age)
)

# Commit and close
conn.commit()
conn.close()

print("User created successfully!")
