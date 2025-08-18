import sqlite3
from user_property import User, Property
import json
import os

DB_FILE = "rentals.db"
PROPERTIES_JSON = "properties.json"
USERS_JSON = "users.json"


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        group_size INTEGER,
        preferred_environment TEXT,  -- comma-separated
        must_have_feature TEXT,      -- comma-separated
        budget REAL
    )""")
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
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO users (user_id, name, group_size, preferred_environment, must_have_feature, budget)
    VALUES (?, ?, ?, ?, ?, ?)""",
    (user.user_id, user.name, user.group_size, user.preferred_environment, user.must_have_feature, user.budget))
    conn.commit()
    conn.close()


def insert_property(prop: Property):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO properties (property_id, name, location, allowed_number_check_in, type, price_per_night, features, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    (prop.property_id, prop.name, prop.location, prop.allowed_number_check_in, prop.type, prop.price_per_night, prop.features, prop.tags))
     # ",".join(prop.features), ",".join(prop.tags) ))
    conn.commit()
    conn.close()


def load_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, group_size, preferred_environment, must_have_feature, budget FROM users")
    rows = cur.fetchall()
    conn.close()
    return [User(*row) for row in rows]


def load_properties():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT property_id, name, location, allowed_number_check_in, type, price_per_night, features, tags FROM properties")
    rows = cur.fetchall()
    print('rows in property res')
    print(rows)
    conn.close()

    print('before return ')
    print([Property(*row) for row in rows])
    return [Property(*row) for row in rows]
    # properties = []
    # for row in rows:
    #     features = row[6].split(",") if row[6] else []
    #     tags = row[7].split(",") if row[7] else []
    #     properties.append(Property(row[0], row[1], row[2], row[3], row[4], row[5], features, tags))
    #
    # return properties


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
