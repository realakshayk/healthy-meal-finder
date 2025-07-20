# utils/freeform_query_parser.py

import re
from typing import Dict, Optional

# Define basic keyword sets for meal types and dietary preferences
MEAL_TYPES = [
    "breakfast", "lunch", "dinner", "brunch", "snack", "dessert"
]

DIETARY_PREFERENCES = {
    "low-carb": ["low carb", "low-carb", "keto", "ketogenic"],
    "high-protein": ["high protein", "protein-rich", "muscle gain", "bulking"],
    "vegan": ["vegan", "plant-based", "no animal products"],
    "vegetarian": ["vegetarian", "no meat", "meatless"],
    "gluten-free": ["gluten free", "gluten-free"],
    "paleo": ["paleo"],
    "weight-loss": ["weight loss", "lose weight", "fat loss", "cutting"],
    "balanced": ["balanced", "healthy", "wellness", "maintenance"]
}

LOCATION_KEYWORDS = ["near me", "close by", "nearby", "around here", "in my area"]

CALORIE_PATTERN = re.compile(r"under (\d+) calories|less than (\d+) calories|below (\d+) calories", re.IGNORECASE)


def parse_freeform_query(query: str) -> Dict[str, Optional[str]]:
    """
    Parse a freeform meal search query into structured filters.
    Returns a dict with keys: meal_type, dietary_preference, location, calorie_limit, raw_query
    """
    query_lower = query.lower()
    result = {
        "meal_type": None,
        "dietary_preference": None,
        "location": None,
        "calorie_limit": None,
        "raw_query": query
    }

    # Meal type
    for meal in MEAL_TYPES:
        if meal in query_lower:
            result["meal_type"] = meal
            break

    # Dietary preference
    for pref, keywords in DIETARY_PREFERENCES.items():
        for kw in keywords:
            if kw in query_lower:
                result["dietary_preference"] = pref
                break
        if result["dietary_preference"]:
            break

    # Location intent
    for loc_kw in LOCATION_KEYWORDS:
        if loc_kw in query_lower:
            result["location"] = "near_me"
            break

    # Calorie limit
    cal_match = CALORIE_PATTERN.search(query_lower)
    if cal_match:
        for group in cal_match.groups():
            if group:
                result["calorie_limit"] = int(group)
                break

    return result 