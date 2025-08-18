import sqlite3
from user_property import User, Property
import json
import os
from contextlib import contextmanager

DB_FILE = "../rentals.db"
PROPERTIES_JSON = "properties.json"
USERS_JSON = "users.json"


# Context manager for database connection
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

## check NOT NULL
def create_tables():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            group_size INTEGER NOT NULL CHECK(group_size >= 1),
            preferred_environment TEXT NOT NULL,
            budget REAL NOT NULL CHECK(budget >= 0)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            property_id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            type TEXT NOT NULL,
            price_per_night REAL NOT NULL CHECK(price_per_night >= 0),
            features TEXT,
            tags TEXT
        )""")


def insert_user(user: User):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO users (user_id, name, group_size, preferred_environment, budget)
        VALUES (?, ?, ?, ?, ?)""",
                    (user.user_id, user.name, user.group_size, user.preferred_environment,
                     user.budget))


def insert_property(prop: Property):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO properties (property_id, location, type, price_per_night, features, tags)
        VALUES (?, ?, ?, ?, ?, ?)""",
                    (prop.property_id, prop.location, prop.type, prop.price_per_night,
                     ",".join(prop.features), ",".join(prop.tags)))


def load_users():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, name, group_size, preferred_environment, budget FROM users")
        rows = cur.fetchall()
    return [User(*row) for row in rows]


def load_properties():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT property_id, location, type, price_per_night, features, tags FROM properties")
        rows = cur.fetchall()
    properties = []
    for row in rows:
        features = row[4].split(",") if row[4] else []
        tags = row[5].split(",") if row[5] else []
        properties.append(Property(row[0], row[1], row[2], row[3], features, tags))
    return properties


def delete_user(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))


def is_table_empty(table_name: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
    return count == 0


def load_json_to_db():
    """Load data from JSON files into DB tables if tables are empty."""
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


## query property
def query_properties(budget=None, environment=None):
    query = "SELECT * FROM properties WHERE 1=1"
    params = []
    if budget is not None:
        query += " AND price_per_night <= ?"
        params.append(budget)
    if environment is not None:
        query += " AND ? IN (SELECT value FROM json_each(tags))"
        params.append(environment)
    with get_conn() as conn:
        return conn.execute(query, params).fetchall()