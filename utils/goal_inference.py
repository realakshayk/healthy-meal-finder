# utils/goal_inference.py
import os
import logging
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GOAL_IDS = ["muscle_gain", "weight_loss", "keto", "balanced"]
GOAL_NAMES = {
    "muscle_gain": "Muscle Gain",
    "weight_loss": "Weight Loss",
    "keto": "Keto",
    "balanced": "Balanced"
}

class GoalInference:
    """
    Utility for inferring the most likely fitness goal from a meal description using OpenAI.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found. Goal inference will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def infer_goal(self, meal_description: str) -> Dict[str, Optional[str]]:
        """
        Infer the most likely fitness goal for a meal description.
        Returns a dict with goal_id, goal_name, confidence_score, and explanation.
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback inference.")
            return self._fallback_inference(meal_description)
        try:
            prompt = self._create_goal_inference_prompt(meal_description)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a nutrition and fitness expert. Given a meal description, infer which fitness goal it best matches. Only choose from: muscle_gain, weight_loss, keto, balanced. Return a JSON object with keys: goal_id, goal_name, confidence_score (0-100), and explanation. Be concise and realistic. If unsure, choose 'balanced' with lower confidence."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()
            import json
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                data = json.loads(json_str)
                # Normalize output
                goal_id = data.get("goal_id")
                if goal_id not in GOAL_IDS:
                    goal_id = "balanced"
                return {
                    "goal_id": goal_id,
                    "goal_name": GOAL_NAMES.get(goal_id, goal_id),
                    "confidence_score": int(data.get("confidence_score", 60)),
                    "explanation": data.get("explanation", "")
                }
            else:
                raise ValueError("No JSON found in OpenAI response")
        except Exception as e:
            logger.error(f"Error inferring goal: {e}")
            return self._fallback_inference(meal_description)

    def _create_goal_inference_prompt(self, meal_description: str) -> str:
        return f"""Given this meal description, infer the most likely fitness goal (muscle_gain, weight_loss, keto, balanced):\n\nMeal: {meal_description}\n\nReturn a JSON object with keys: goal_id, goal_name, confidence_score (0-100), and explanation."""

    def _fallback_inference(self, meal_description: str) -> Dict[str, Optional[str]]:
        desc = meal_description.lower()
        if any(word in desc for word in ["chicken", "beef", "steak", "protein", "muscle", "gain", "bulk"]):
            return {"goal_id": "muscle_gain", "goal_name": "Muscle Gain", "confidence_score": 70, "explanation": "High protein or muscle-building keywords detected."}
        if any(word in desc for word in ["keto", "bacon", "avocado", "fat", "low carb", "ketogenic"]):
            return {"goal_id": "keto", "goal_name": "Keto", "confidence_score": 70, "explanation": "Low-carb or high-fat keywords detected."}
        if any(word in desc for word in ["salad", "light", "low calorie", "weight loss", "slim", "cutting"]):
            return {"goal_id": "weight_loss", "goal_name": "Weight Loss", "confidence_score": 65, "explanation": "Low-calorie or weight loss keywords detected."}
        return {"goal_id": "balanced", "goal_name": "Balanced", "confidence_score": 60, "explanation": "No strong indicators; defaulting to balanced."}

# Global instance
goal_inference = GoalInference() 