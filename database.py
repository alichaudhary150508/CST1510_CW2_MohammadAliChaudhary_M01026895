import sqlite3
from models.user import User

DB_PATH = "DATA/users.db"

def init_db():
    """Initialize the SQLite database and create the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            hashed_password TEXT,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_user_to_db(user: User):
    """Add a User object to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO users (username, hashed_password, email, first_name, last_name)
        VALUES (?, ?, ?, ?, ?)
    """, (user.username, user.password, user.email, user.first_name, user.last_name))

    conn.commit()
    conn.close()


def get_user_from_db(username: str):
    """Retrieve a user from the database by their username."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = c.fetchone()

    conn.close()

    # If user data exists, return a User object
    if user_data:
        return User(
            username=user_data[1],  # username is at index 1
            email=user_data[3],     # email is at index 3
            password=user_data[2],  # password is at index 2
            first_name=user_data[4],# first_name is at index 4
            last_name=user_data[5]  # last_name is at index 5
        )
    return None
