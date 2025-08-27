import streamlit as st
from streamlit_lottie import st_lottie
import requests
from user_property import User, Property
import pandas as pd
import database
from recommender import get_recommendations

# -------------------------------
# Helper functions for display
# -------------------------------

def display_user(user):
    with st.container():
        st.markdown(
            """
            <div style="
                border: 1px solid #444;          
                border-radius: 12px;            
                padding: 15px;
                margin-bottom: 15px;
                background-color: #1e1e1e;       
                box-shadow: 2px 2px 8px rgba(0,0,0,0.6);  
                color: #eee;                     

            ">
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1.5, 3])  

        with col1:
            st.markdown("**ID:**")
            st.markdown("**Name:**")
            st.markdown("**Group Size:**")
            st.markdown("**Preferred Environment:**")
            st.markdown("**Must-have Feature:**")
            st.markdown("**Budget:**")

        with col2:
            st.write(user.user_id)
            st.write(user.name)
            st.write(user.group_size)
            st.write(", ".join(user.preferred_environment) if isinstance(user.preferred_environment, list) else user.preferred_environment)
            st.write(", ".join(user.must_have_feature) if isinstance(user.must_have_feature, list) else user.must_have_feature)
            st.write(f"${user.budget}")

        st.markdown("</div>", unsafe_allow_html=True)

def display_property(prop):
    # features_str = ", ".join(prop.features)
    # tags_str = ", ".join(prop.tags)
    
    image_url = getattr(prop, "image_url", "https://upload.wikimedia.org/wikipedia/commons/5/54/Toronto_Cabbage_Town_1_%288437347293%29.jpg")
    rating = getattr(prop, "rating", 4.5)
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    
    card_html = f"""
    <div style="
        border: 1px solid #444;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
        background-color: #1e1e1e;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.6);
        color: #eee;
        max-width: 300px;
    ">
        <img src="{image_url}" style="width:100%; border-radius:12px; margin-bottom:10px;">
        <h4 style="margin:0;">{prop.name} ({prop.type.title()})</h4>
        <p style="margin:3px 0;">Location: {prop.location}</p>
        <p style="margin:3px 0;">Price per night: ${prop.price_per_night:.2f}</p>
        <p style="margin:3px 0;">Number of persons allowed to check-in: {prop.allowed_number_check_in}</p>
        <p style="margin:3px 0;">Rating: <span style='color: gold;'>{stars}</span></p>
        <p style="margin:3px 0;"><strong>Features:</strong> {prop.features}</p>
        <p style="margin:3px 0;"><strong>Tags:</strong> {prop.tags}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def display_properties_grid(properties, cols_per_row=3):
    for i in range(0, len(properties), cols_per_row):
        row_props = properties[i:i+cols_per_row]
        # Always create exactly `cols_per_row` columns
        cols_streamlit = st.columns(cols_per_row)
        
        for j, col in enumerate(cols_streamlit):
            with col:
                if j < len(row_props):
                    display_property(row_props[j])
                else:
                    # Empty column to preserve layout
                    st.markdown("<div style='height: 1px;'></div>", unsafe_allow_html=True)
    # -------------------------------
# Main app
# -------------------------------

def main():
    st.title("🏖️ Vacation Rental Recommender")

    # Custom CSS animations
    st.markdown(
        """
        <style>
        /* Fade-in animation for property cards */
        .fade-in {
            animation: fadeIn 1.5s ease-in;
        }
        @keyframes fadeIn {
            0% {opacity: 0; transform: translateY(10px);}
            100% {opacity: 1; transform: translateY(0);}
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize database and load data
    database.create_tables()
    database.load_json_to_db()
    users = database.load_users()
    properties = database.load_properties()


    # Function to fetch lottie JSON
    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            st.warning(f"Failed to load animation from {url}")
            return None
        return r.json()

    # Load animation
    lottie_animation = load_lottieurl("https://raw.githubusercontent.com/lamanam/vacation_rental_recommender/refs/heads/main/Enjoy%20Beach%20Vacation.json")

    menu = ["Home", "Create User", "View Users", "Delete User", "View Properties", "Get Recommendations"]
    choice = st.sidebar.selectbox("Menu", menu)

    # -------------------------------
    # Home Page
    # -------------------------------
    if choice == "Home":
        st.markdown(
        """
        <div style="text-align: center; padding: 40px;">
            <h1 style="color:#ffcc00; font-size: 36px; margin-bottom: 10px;">
                🌴 Welcome to Team Shier's Vacation Rental Recommender 🌴
            </h1>
             <h2 style="color:#ffcc00; font-weight: bold; font-style: italic;">
                ✨ Your dream vacation starts here ✨
            </h2>
            <h3 style="color:#cccccc; font-weight: normal;">
                Find the perfect stay tailored to your preferences
            </h3>
            <p style="font-size: 18px; color:#aaaaaa; margin-top: 30px;">
                Use the sidebar menu to:
            </p>
            <ul style="text-align:left; display:inline-block; color:#dddddd; font-size:18px;">
                <li>👤 <strong>Create User</strong> – Add your profile to get recommendations</li>
                <li>📋 <strong>View Users</strong> – See all registered users</li>
                <li>❌ <strong>Delete User</strong> – Remove a user</li>
                <li>🏡 <strong>View Properties</strong> – Browse rental listings</li>
                <li>🎯 <strong>Get Recommendations</strong> – Personalized suggestions for you</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

        # Add animation
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=600, height=400, key="beach_vacation")
        else:
            st.info("🎬 Animation failed to load!")



    # -------------------------------
    # Create User
    # -------------------------------
    elif choice == "Create User":
        st.subheader("Create a New User Profile")
        user_id = st.number_input("User ID (integer)", min_value=1, step=1)
        name = st.text_input("Name")
        group_size = st.number_input("Group size", min_value=1, step=1)
        preferred_env = st.multiselect("Preferred environment", ["mountain", "lake", "beach", "city"])
        must_have_feature = st.multiselect("Must have feature", ['balcony', 'canoe', 'fireplace', 'garden', 'hiking trails', 'hot tub', 'kitchen', 'lake access', 'mountain view', 'ocean view', 'parking', 'ski-in/ski-out', 'vineyard view', 'wifi'])
        budget = st.number_input("Budget", min_value=0, step=10)

        if st.button("Create User"):
            user = User(user_id, name, group_size, preferred_env, must_have_feature, budget)
            database.insert_user(user)
            users = database.load_users()
            st.success(f"User {name} created successfully! 🎉")
            st.balloons()  # Balloons animation 🎈

    # -------------------------------
    # View Users
    # -------------------------------
    elif choice == "View Users":
        st.subheader("All Users")
        if not users:
            st.info("No users found.")
        else:
            for u in users:
                display_user(u)

    # -------------------------------
    # Delete User
    # -------------------------------
    elif choice == "Delete User":
        st.subheader("Delete User Profile")
        del_id = st.number_input("Enter User ID to delete", min_value=1, step=1)
        if st.button("Delete User"):
            database.delete_user(del_id)
            st.success(f"User {del_id} deleted (if existed).")

    # -------------------------------
    # View Properties
    # -------------------------------
    elif choice == "View Properties":
        st.subheader("All Properties")

        if "properties" not in st.session_state:
            st.session_state.properties = database.load_properties()

        props = st.session_state.properties

        if not props:
            st.info("No properties found.")
        else:
            # Add fade-in wrapper
            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            display_properties_grid(props, cols_per_row=3)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Get Recommendations
    # -------------------------------
    elif choice == "Get Recommendations":
        st.subheader("Get Property Recommendations")
        rec_user_id = st.number_input("Enter your User ID", min_value=1, step=1)
        top_n = st.number_input(
        "Enter the maximum number of recommendations you want", min_value=1, step=1, value=5   # 👈 default shown when the app first runs
        )
        if st.button("Get Recommendations"):
            user = next((u for u in users if u.user_id == rec_user_id), None)
            if not user:
                st.error("User not found.")
            else:
                recs = get_recommendations(user, properties, top_n)
                if not recs:
                    st.info("No suitable properties found for you.")
                else:
                    st.success(f"Top {len(recs)} recommendations for {user.name}:")
                    st.snow()  # ❄️ Snow animation
                    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                    display_properties_grid(recs)
                    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()