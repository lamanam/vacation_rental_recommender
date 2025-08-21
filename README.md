# Team 12 Repo for RSM8431Y Python Project - Vacation Rental Recommender

## Project Description

This project is a **Vacation Rental Recommender System** built with Python and Streamlit.
It allows users to input their preferences (budget, group size, must have features, etc.) and returns personalized vacation rental recommendations based on our curated dataset and recommendation logic.

---

## File Structure

* `app_streamlit.py` → Main Streamlit web app
* `user_property.py` → Defines User and Property classes
* `database.py` → Handles database connections and queries
* `recommender.py` → Recommendation logic
* `rentals.db` → SQLite database of rental properties
* `requirements.txt` → Python library dependencies
* `properties.json` → Raw property dataset

*(extra helper files or copies are ignored here for clarity)*

---

## How to Run the Web App

1. Clone the repository to your local machine:

   ```bash
   git clone <repo-url>
   cd vacation_rental_recommender
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv_rental
   ```

3. Activate the virtual environment:

   * macOS/Linux:

     ```bash
     source venv_rental/bin/activate
     ```
   * Windows (PowerShell):

     ```powershell
     venv_rental\Scripts\activate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the Streamlit web app (**Make sure you delete the rentals.db before run every time you updated the properties.json file**):

   ```bash
   streamlit run app_streamlit.py
   ```

6. The app will open automatically in your browser at:

   ```
   http://localhost:8501
   ```

7. When finished, deactivate the virtual environment:

   ```bash
   deactivate
   ```



