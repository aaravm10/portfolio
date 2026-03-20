import json
import sqlite3

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_db():
    """Initialize the database tables"""
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                favorite_team TEXT,
                favorite_player TEXT,
                friends TEXT,
                watchlist TEXT
            )
        """)
        # Migration: add watchlist column if it doesn't exist
        try:
            conn.execute("ALTER TABLE users ADD COLUMN watchlist TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.commit()
    finally:
        conn.close()


def get_watchlist(user_id):
    """Get user's watchlist as a list of player names"""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT watchlist FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row and row["watchlist"]:
            return json.loads(row["watchlist"])
        return []
    finally:
        conn.close()


def add_to_watchlist(user_id, player_name):
    """Add a player to user's watchlist. Returns True if added, False if already present."""
    watchlist = get_watchlist(user_id)
    if player_name in watchlist:
        return False
    watchlist.append(player_name)
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE users SET watchlist = ? WHERE id = ?",
            (json.dumps(watchlist), user_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def remove_from_watchlist(user_id, player_name):
    """Remove a player from user's watchlist. Returns True if removed, False if not present."""
    watchlist = get_watchlist(user_id)
    if player_name not in watchlist:
        return False
    watchlist.remove(player_name)
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE users SET watchlist = ? WHERE id = ?",
            (json.dumps(watchlist), user_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    if not username or not password:
        return None
    
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, name FROM users WHERE name = ? AND password = ?",
            (username, password)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def user_exists(username):
    """Check if a user exists"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT 1 FROM users WHERE name = ?", 
            (username,)
        ).fetchone()
        return user is not None
    finally:
        conn.close()

def register_user(username, password):
    """Register a new user"""
    if not username or not password:
        return False, "Username and password required"
    
    if user_exists(username):
        return False, "Username already exists"
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True, "Account created successfully"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, name, favorite_team, favorite_player FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, name, favorite_team, favorite_player FROM users WHERE name = ?",
            (username,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()