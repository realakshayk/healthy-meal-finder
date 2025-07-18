# app.py

import streamlit as st
import httpx
from streamlit_js_eval import streamlit_js_eval

API_URL = "http://127.0.0.1:8000/find-meals"

st.set_page_config(page_title="Healthy Meal Finder", layout="centered")

st.title("🥗 Healthy Meal Finder")
st.subheader("Find healthy restaurants near you based on your fitness goals")

# --- Step 1: Get User's Geolocation ---
coords = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location"
)

if coords and "coords" in coords:
    user_lat = coords["coords"]["latitude"]
    user_lon = coords["coords"]["longitude"]
    st.success(f"📍 Location found: {user_lat:.4f}, {user_lon:.4f}")
else:
    st.warning("Using default location (New York, NY)")
    user_lat = 40.7128
    user_lon = -74.0060

# --- Step 2: User Input ---
with st.form("restaurant_form"):
    goal = st.selectbox("Fitness Goal", ["muscle_gain", "weight_loss", "keto", "balanced"])
    radius = st.slider("Search Radius (miles)", 1, 10, 3)

    submitted = st.form_submit_button("Find Restaurants")

# --- Step 3: Call Backend and Display Results ---
if submitted:
    with st.spinner("Looking for nearby healthy restaurants..."):
        try:
            payload = {
                "lat": user_lat,
                "lon": user_lon,
                "goal": goal,
                "radius_miles": radius
            }

            response = httpx.post(API_URL, json=payload)
            response.raise_for_status()

            restaurants = response.json().get("meals", [])  # Still using "meals" key
            if not restaurants:
                st.warning("No matching restaurants found.")
            else:
                st.success(f"Found {len(restaurants)} restaurant(s):")

                for r in restaurants:
                    st.markdown(f"""
                    ### 🍽️ {r['name']}
                    **Rating:** {r.get('rating', '?')} ⭐️  
                    **Address:** {r.get('address', 'N/A')}  
                    ---
                    """)

        except Exception as e:
            st.error(f"Error: {e}")
