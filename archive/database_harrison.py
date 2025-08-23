import sqlite3
from user_property import User, Property
import json
import os

DB_FILE = "../rentals.db"
PROPERTIES_JSON = "canadian_properties_300.json"
USERS_JSON = "users.json"


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        group_size INTEGER,
        preferred_environment TEXT,
        budget_range REAL,
        travel_dates TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        property_id INTEGER PRIMARY KEY,
        name TEXT,
        location TEXT,
        type TEXT,
        price_per_night REAL,
        features TEXT,
        tags TEXT
    )""")
    conn.commit() # This method is used to ensure that the above staged changes are permanently written into the database
    conn.close()


def insert_user(user: User):
     # Convert budget_range list to a comma-separated string
    budget_str = ",".join(map(str, user.budget_range))
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO users (user_id, name, group_size, preferred_environment, budget_range, travel_dates)
    VALUES (?, ?, ?, ?, ?, ?)""",
    (user.user_id, user.name, user.group_size, user.preferred_environment, budget_str, user.travel_dates)) # Parameter Binding
    conn.commit()
    conn.close()


def insert_property(prop: Property):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO properties (property_id, name, location, type, price_per_night, features, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?)""",
    (prop.property_id, prop.name, prop.location, prop.type, prop.price_per_night,
     ",".join(prop.features), ",".join(prop.tags)))
    conn.commit()
    conn.close()


def load_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, group_size, preferred_environment, budget_range, travel_dates FROM users")
    rows = cur.fetchall()
    conn.close()
    return [User(*row) for row in rows]  # We are fetching data of users from the DB file and store them as User objects in a LIST called properties 
    # * is used for unpacking iterables in Python


def load_properties():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT property_id, name, location, type, price_per_night, features, tags FROM properties")
    rows = cur.fetchall()
    conn.close()
    properties = [] # We are fetching data of properties from the DB file and store them as Property objects in a LIST called properties 
    for row in rows:
        properties.append(Property(
        row[0],  # property_id
        row[1],  # name
        row[2],  # location
        row[3],  # type
        row[4],  # price_per_night
        row[5].split(",") if row[5] else [],  # features
        row[6].split(",") if row[6] else []   # tags
        ))
    return properties


def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_table_empty(table_name: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    conn.close()
    return count == 0


def load_json_to_db():
    """Load data from JSON files into DB tables if tables are empty."""
    # Load properties from JSON
    if os.path.exists(PROPERTIES_JSON):
        with open(PROPERTIES_JSON, "r") as f:
            props_data = json.load(f)
        for p_dict in props_data:
            prop = Property.from_dict(p_dict)
            insert_property(prop)
        print(f"Loaded {len(props_data)} properties from JSON into DB.")

    # Load users from JSON
    if os.path.exists(USERS_JSON):
        with open(USERS_JSON, "r") as f:
            users_data = json.load(f)
        for u_dict in users_data:
            user = User.from_dict(u_dict)
            insert_user(user)
        print(f"Loaded {len(users_data)} users from JSON into DB.")

if __name__ == "__main__":
    create_tables()
    load_json_to_db()