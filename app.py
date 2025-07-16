# app.py

import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000/find-meals"

st.set_page_config(page_title="Healthy Meal Finder", layout="centered")

st.title("🥗 Healthy Meal Finder")
st.subheader("Find restaurant meals that fit your fitness goals")

with st.form("meal_form"):
    location = st.text_input("Location", value="New York, NY")
    goal = st.selectbox("Fitness Goal", ["muscle_gain", "weight_loss", "keto", "balanced"])
    radius = st.slider("Search Radius (miles)", 1, 10, 3)

    submitted = st.form_submit_button("Find Meals")

if submitted:
    with st.spinner("Looking for meals..."):
        try:
            payload = {
                "location": location,
                "goal": goal,
                "radius_miles": radius
            }

            response = httpx.post(API_URL, json=payload)
            response.raise_for_status()

            meals = response.json().get("meals", [])
            if not meals:
                st.warning("No matching meals found.")
            else:
                st.success(f"Found {len(meals)} meal(s):")

                for meal in meals:
                    st.markdown(f"""
                        ### 🍴 {meal['dish']}
                        **Restaurant:** {meal['restaurant']}  
                        **Calories:** {meal['calories']} kcal  
                        **Protein:** {meal['protein']}g  
                        **Carbs:** {meal['carbs']}g  
                        **Fat:** {meal['fat']}g  
                        **Score:** {meal['score']}  
                        ---
                    """)

        except Exception as e:
            st.error(f"Error: {e}")
