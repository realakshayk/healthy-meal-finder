# main.py

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from services.meal_service import find_meals

# --- Logging Config ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# --- Valid Fitness Goals ---
VALID_GOALS = {"muscle_gain", "weight_loss", "keto", "balanced"}

# --- FastAPI App ---
app = FastAPI()

# --- Request Model ---
class UserRequest(BaseModel):
    location: str
    goal: str = Field(..., description="One of: muscle_gain, weight_loss, keto, balanced")
    radius_miles: float = Field(..., gt=0, description="Must be a positive number")

    @validator("goal")
    def validate_goal(cls, v):
        if v not in VALID_GOALS:
            raise ValueError(f"Invalid goal: '{v}'. Must be one of {', '.join(VALID_GOALS)}.")
        return v

# --- API Endpoint ---
@app.post("/find-meals")
def find_meals_api(request: UserRequest):
    meals = find_meals(
        location=request.location,
        goal=request.goal,
        radius_miles=request.radius_miles
    )
    return {"meals": meals}
