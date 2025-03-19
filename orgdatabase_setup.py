import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("organisation.db")
c = conn.cursor()

# Table for storing users (hashed passwords for security)
c.execute('''CREATE TABLE IF NOT EXISTS organisation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orgname TEXT UNIQUE,
    password TEXT
)''')

# Table for storing login activity
c.execute('''CREATE TABLE IF NOT EXISTS login_activity_organisation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orgname TEXT,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Insert admin account
admin_password = generate_password_hash("admin123")  # Hash the password
c.execute("INSERT OR IGNORE INTO users (orgname, password) VALUES (?, ?)", ("admin", admin_password))

conn.commit()
conn.close()
