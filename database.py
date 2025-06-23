import sqlite3

DB_NAME = 'journal.db'
# This file contains the database connection and initialization logic for the Daily Journal application.
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn

# This function initializes the database and creates the journal_entries table if it doesn't exist.
# It should be called once when the application starts to ensure the database is ready for use.
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mood TEXT,
            entry TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
