import sqlite3
from user_property import User, Property
import json
import os

## Rename the SQLite database and JSON filenames
DB_FILE = "rentals.db"
PROPERTIES_JSON = "properties.json"
USERS_JSON = "users.json"


def create_tables():
    """
    Create the required SQLite tables if they do not exist.
    Tables:
        users:
            user_id (INTEGER PRIMARY KEY)
            name (TEXT)
            group_size (INTEGER)
            preferred_environment (TEXT)   -- comma-separated if multiple values
            must_have_feature (TEXT)       -- comma-separated if multiple values
            budget (REAL)

        properties:
            property_id (INTEGER PRIMARY KEY)
            name (TEXT)
            location (TEXT)
            allowed_number_check_in (INTEGER) -- maximum group size allowed
            type (TEXT)
            price_per_night (REAL)
            features (TEXT)   -- comma-separated list of features
            tags (TEXT)       -- comma-separated list of tags
    """
    conn = sqlite3.connect(DB_FILE) # open connection to SQLite database
    cur = conn.cursor()
    # Create the 'users' table with basic profile fields and preferences
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        group_size INTEGER,
        preferred_environment TEXT,  -- comma-separated
        must_have_feature TEXT,      -- comma-separated
        budget REAL
    )""")
    # Create the 'properties' table with basic information and details
    cur.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        property_id INTEGER PRIMARY KEY,
        name TEXT,
        location TEXT,
        allowed_number_check_in INTEGER,  -- NEW field
        type TEXT,
        price_per_night REAL,
        features TEXT,  -- comma-separated
        tags TEXT       -- comma-separated
    )""")
    conn.commit()
    conn.close()


def insert_user(user: User):
    """
        Insert or update a user record in the 'users' table
        If a user_id already exists,
        the old record is replaced with the new one.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Insert or replace a user row with values from the User object
    cur.execute("""
    INSERT OR REPLACE INTO users (user_id, name, group_size, preferred_environment, must_have_feature, budget)
    VALUES (?, ?, ?, ?, ?, ?)""",
    (user.user_id, user.name, user.group_size, json.dumps(user.preferred_environment),json.dumps(user.must_have_feature), user.budget))
    conn.commit()
    conn.close()


def insert_property(prop: Property):
    """
            Insert or update a property record in the 'properties' table
            If a property_id already exists,
            the old record is replaced with the new one.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Insert or replace a property row with values from the Property object
    cur.execute("""
    INSERT OR REPLACE INTO properties 
    (property_id, name, location, allowed_number_check_in, type, price_per_night, features, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    (
        prop.property_id,
        prop.name,
        prop.location,
        prop.allowed_number_check_in,
        prop.type,
        prop.price_per_night,
        prop.features,
        prop.tags
    ))
    conn.commit()
    conn.close()


def load_users():
    """
        Load all user records from the 'users' table.
        Returns a list of User objects, each created from a row in the table.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, group_size, preferred_environment, must_have_feature, budget FROM users")
    rows = cur.fetchall()
    conn.close()

    users = []
    for row in rows:
        user_id, name, group_size, preferred_environment, must_have_feature, budget = row
        users.append(User(
            user_id,
            name,
            group_size,
            json.loads(preferred_environment) if preferred_environment else [],
            json.loads(must_have_feature) if must_have_feature else [],
            budget
        ))
    return users


def load_properties():
    """
            Load all property records from the 'properties' table.
            Returns a list of Property objects, each created from a row in the table.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    SELECT property_id, name, location, allowed_number_check_in, type, price_per_night, features, tags 
    FROM properties
    """)
    rows = cur.fetchall()
    conn.close()
    return [Property(*row) for row in rows]


def delete_user(user_id):
    """
    Delete a user record in the 'users' table based on the given user ID.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Delete the user with the given user_id; no effect if user_id not present
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_table_empty(table_name: str) -> bool:
    """
    Check if a given table in the database is empty.
    Returns True if empty, False otherwise.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}") # Count how many rows exist in the given table
    count = cur.fetchone()[0]
    conn.close()
    return count == 0


def load_json_to_db():
    """
    Load data from JSON files into DB tables if tables are empty.
    Inserts records into the database and prints the number of rows loaded.
    """
    # Load properties from JSON
    if os.path.exists(PROPERTIES_JSON) and is_table_empty("properties"):
        with open(PROPERTIES_JSON, "r") as f:
            props_data = json.load(f)
        for p_dict in props_data:
            prop = Property.from_dict(p_dict)
            insert_property(prop)
        print(f"Loaded {len(props_data)} properties from JSON into DB.")

    # Load users from JSON
    if os.path.exists(USERS_JSON) and is_table_empty("users"):
        with open(USERS_JSON, "r") as f:
            users_data = json.load(f)
        for u_dict in users_data:
            user = User.from_dict(u_dict)
            insert_user(user)
        print(f"Loaded {len(users_data)} users from JSON into DB.")
