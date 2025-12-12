import sqlite3
from pathlib import Path

DATA_DIR = Path("DATA")
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "DATA/intelligence.db" # Path

def connect_database(db_path=DB_PATH):
    """
    Connects to a SQLite database,
    Creates the DB file if it doesn't exist
    """

    return sqlite3.connect(str(db_path))