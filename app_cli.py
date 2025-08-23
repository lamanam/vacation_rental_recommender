# app.py

from user_property import User
import database
from recommender import get_recommendations

def print_user(user):
    print(f"ID: {user.user_id} | Name: {user.name} | Group: {user.group_size} | Env: {user.preferred_environment} | Must Have Features: {user.must_have_feature}  | Budget: ${user.budget}")


def print_property(prop):
    print(f"ID: {prop.property_id} | {prop.name} | {prop.type} in {prop.location} | ${prop.price_per_night}/night  | {prop.features} | {prop.tags}")
    # print(f"  Features: {', '.join(prop.features)}")
    # print(f"  Tags: {', '.join(prop.tags)}")


def main():
    
    # step 1: create db tables if they don't exist
    database.create_tables()
    print('Created tables')

    # step 2: If tables are empty - load from sample json for each users and properties
    database.load_json_to_db()
    print('Loaded users & properties from json')

    # step 3: get all users and properties in the db 
    users = database.load_users()
    properties = database.load_properties()
    print('extracted users list ... num of users ', len(users))
    print('extracted properties list ... num of properties ', len(properties))
    
    # step 4: options inf loop
    while True:
        print("\n=== Vacation Rental Recommender ===")
        print("1. Create User Profile")
        print("2. View All Users")
        print("3. Delete User Profile")
        print("4. View Properties")
        print("5. Get Recommendations")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            # Create user
            try:
                user_id = int(input("User ID (integer): "))
                name = input("Name: ")
                group_size = int(input("Group size: "))
                preferred_env = input("Preferred environment (mountain, lake, beach, city): ").lower()
                budget = float(input("Budget per night: "))
                must_have_feats = input("Must have features (comma separated): ").lower()
            except ValueError:
                print("Invalid input. Please enter correct data types.")
                continue

            user = User(user_id, name, group_size, preferred_env, must_have_feats, budget)
            database.insert_user(user)
            users = database.load_users()  # reload after insert
            print(f"User {name} created.")

        elif choice == "2":
            # View users
            if not users:
                print("No users found.")
            for u in users:
                print_user(u)

        elif choice == "3":
            # Delete user
            try:
                del_id = int(input("Enter User ID to delete: "))
            except ValueError:
                print("Invalid ID")
                continue
            database.delete_user(del_id)
            users = database.load_users()
            print(f"User {del_id} deleted if existed.")

        elif choice == "4":
            # View properties
            if not properties:
                print("No properties found.")
            for p in properties:
                print_property(p)

        elif choice == "5":
            # Get recommendations
            try:
                rec_user_id = int(input("Enter your User ID: "))
            except ValueError:
                print("Invalid ID")
                continue
            user = next((u for u in users if u.user_id == rec_user_id), None)
            if not user:
                print("User not found.")
                continue
            recs = get_recommendations(user, properties)
            if not recs:
                print("No suitable properties found for you.")
            else:
                print(f"\nTop {len(recs)} recommendations for {user.name}:")
                for prop in recs:
                    print_property(prop)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
