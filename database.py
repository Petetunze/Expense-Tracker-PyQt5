import sqlite3

''' Initialize the SQLite database.
    Creates 'users' and 'expenses' tables if they don't exist. '''
def init_db():

    # Connect to the SQLite database file 'expense_tracker.db'.
    # If the file doesn't exist, it will be created.
    # Create a cursor object to execute SQL commands.
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()

    # Create the 'users' table if it doesn't exist.
    # The table has the following columns:
    # - id (primary key, auto-incrementing integer)
    # - username (unique text, not null)
    # - password (text, not null)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # Create the 'expenses' table if it doesn't exist.
    # The table has the following columns:
    # - id (primary key, auto-incrementing integer)
    # - user_id (foreign key referencing the 'users' table, not null)
    # - name (text, not null)
    # - cost (real, not null)
    # - date (text, not null)
    # - description (text)
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            cost REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Commit changes and close the connection.
    conn.commit()
    return conn
