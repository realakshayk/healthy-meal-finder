import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/meals/find"
FREEFORM_URL = "http://localhost:8000/api/v1/meals/freeform-search"

st.set_page_config(page_title="Healthy Meal Finder", page_icon="🥗", layout="centered")
st.title("🥗 Healthy Meal Finder")

# --- Sidebar for API Key ---
st.sidebar.header("API Key Settings")
api_key = st.sidebar.text_input("X-API-Key", value="your_partner_key", type="password", help="Enter your API key to access the meal finder API.")

st.markdown("""
Enter your location and fitness goal to get healthy meal recommendations from local restaurants.
""")

with st.form("meal_finder_form"):
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=40.7128, format="%.6f")
        radius = st.number_input("Search Radius (miles)", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
    with col2:
        lon = st.number_input("Longitude", value=-74.0060, format="%.6f")
        goal = st.selectbox(
            "Fitness Goal",
            ["muscle_gain", "weight_loss", "keto", "balanced"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    submitted = st.form_submit_button("Find Meals")

def display_meals(meals, section_title=None):
    if section_title:
        st.subheader(section_title)
    for meal in meals:
        # Card-style layout using columns
        card = st.container()
        with card:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"### 🍽️ {meal.get('dish_name', 'Unknown Dish')}")
                st.markdown(f"**🏢 Restaurant:** {meal.get('restaurant', 'N/A')}")
                st.markdown(f"**📍 Distance:** {meal.get('distance_miles', 'N/A')} miles")
            with c2:
                score = meal.get('score', 0)
                score_display = "".join(["⭐" for _ in range(int(score))])
                score_display += "☆" * (3 - int(score))
                st.markdown(f"**Score:** {score_display} ({score}/3)")
            st.markdown("---")
            nutrition = meal.get('nutrition_facts', {})
            if nutrition:
                n1, n2, n3 = st.columns(3)
                with n1:
                    st.markdown(f"**Calories:**<br>{nutrition.get('calories', 'N/A')}", unsafe_allow_html=True)
                with n2:
                    st.markdown(f"**Protein:**<br>{nutrition.get('protein', 'N/A')}", unsafe_allow_html=True)
                with n3:
                    st.markdown(f"**Carbs:**<br>{nutrition.get('carbohydrates', 'N/A')}", unsafe_allow_html=True)
                st.markdown(f"**Fat:** {nutrition.get('fat', 'N/A')}")
            else:
                st.info("No nutrition facts available.")
            st.markdown("\n")

if submitted:
    st.info("Searching for healthy meals...")
    payload = {
        "lat": lat,
        "lon": lon,
        "goal": goal,
        "radius_miles": radius
    }
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                meals = data["data"].get("meals", [])
                if meals:
                    st.success(f"Found {len(meals)} meal(s) matching your criteria:")
                    display_meals(meals)
                else:
                    st.warning("No meals found for your criteria.")
            else:
                st.error(data.get("message") or "No data returned from API.")
        else:
            try:
                err = response.json()
                st.error(f"API Error: {err.get('detail', response.text)}")
            except Exception:
                st.error(f"API Error: {response.status_code} {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")

# --- Freeform Search Section ---
st.markdown("---")
st.header("🔎 Freeform Meal Search")
st.markdown("""
Type a natural language query (e.g., 'show me low-carb lunch options') to get personalized meal recommendations.
""")

with st.form("freeform_search_form"):
    freeform_query = st.text_input("Enter your meal search query", value="")
    freeform_submitted = st.form_submit_button("Search Meals")

if freeform_submitted:
    if not freeform_query.strip():
        st.warning("Please enter a search query.")
    else:
        st.info("Searching for meals matching your query...")
        payload = {"query": freeform_query}
        headers = {"Content-Type": "application/json", "X-API-Key": api_key}
        try:
            response = requests.post(FREEFORM_URL, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    meals = data["data"].get("meals", [])
                    if meals:
                        st.success(f"Found {len(meals)} meal(s) for your query:")
                        display_meals(meals, section_title="Results for your query:")
                    else:
                        st.warning("No meals found for your query.")
                else:
                    st.error(data.get("message") or "No data returned from API.")
            else:
                try:
                    err = response.json()
                    st.error(f"API Error: {err.get('detail', response.text)}")
                except Exception:
                    st.error(f"API Error: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}") 