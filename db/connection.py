import sqlite3
import os

def get_connection():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "clinique.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Optional: for dict-like access
    return conn
