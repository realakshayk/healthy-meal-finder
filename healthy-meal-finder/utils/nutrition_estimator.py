# utils/nutrition_estimator.py

import os
import json
import logging
from typing import Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class NutritionEstimator:
    """
    Utility for estimating nutrition information from meal descriptions using OpenAI.
    
    This class provides methods to estimate calories, protein, carbs, and fat
    from natural language meal descriptions using OpenAI's GPT models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the nutrition estimator.
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found. Nutrition estimation will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def estimate_nutrition(self, meal_description: str, serving_size: str = "1 serving") -> Dict[str, int]:
        """
        Estimate nutrition information from a meal description.
        Returns a dict with nutrition values and a confidence_score (0-100).
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback estimation")
            nutrition = self._fallback_estimation(meal_description)
            nutrition["confidence_score"] = 70  # Lower confidence for fallback
            return nutrition
        
        try:
            prompt = self._create_nutrition_prompt(meal_description, serving_size)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a nutrition expert. Estimate the nutritional content of meals based on descriptions. 
                        Return ONLY a JSON object with the following structure:
                        {
                            "calories": <estimated calories>,
                            "protein": <protein in grams>,
                            "carbs": <carbohydrates in grams>,
                            "fat": <fat in grams>
                        }
                        
                        Guidelines:
                        - Be realistic and conservative in estimates
                        - Consider typical portion sizes
                        - Protein: 4 calories per gram
                        - Carbs: 4 calories per gram  
                        - Fat: 9 calories per gram
                        - Total calories should roughly equal (protein * 4) + (carbs * 4) + (fat * 9)
                        - Round all values to whole numbers
                        - If unsure, err on the side of higher calories"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()
            nutrition_data = self._parse_nutrition_response(content)
            nutrition_data["confidence_score"] = 95  # High confidence for OpenAI
            logger.info(f"Estimated nutrition for '{meal_description}': {nutrition_data}")
            return nutrition_data
        except Exception as e:
            logger.error(f"Error estimating nutrition: {e}")
            nutrition = self._fallback_estimation(meal_description)
            nutrition["confidence_score"] = 60  # Lower confidence for fallback after error
            return nutrition
    
    def _create_nutrition_prompt(self, meal_description: str, serving_size: str) -> str:
        """
        Create a prompt for nutrition estimation.
        
        Args:
            meal_description: Description of the meal
            serving_size: Serving size information
            
        Returns:
            Formatted prompt for OpenAI
        """
        return f"""Estimate the nutritional content for this meal:

Meal: {meal_description}
Serving Size: {serving_size}

Please provide realistic estimates for:
- Total calories
- Protein (grams)
- Carbohydrates (grams) 
- Fat (grams)

Consider typical portion sizes and cooking methods. Return only the JSON object."""
    
    def _parse_nutrition_response(self, response: str) -> Dict[str, int]:
        """
        Parse the OpenAI response to extract nutrition data.
        
        Args:
            response: Raw response from OpenAI
            
        Returns:
            Dictionary with nutrition values
        """
        try:
            # Try to extract JSON from the response
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                
                data = json.loads(json_str)
                
                # Validate and normalize the data
                nutrition = {
                    "calories": max(0, int(data.get("calories", 0))),
                    "protein": max(0, int(data.get("protein", 0))),
                    "carbs": max(0, int(data.get("carbs", 0))),
                    "fat": max(0, int(data.get("fat", 0)))
                }
                
                # Sanity check: ensure calories make sense
                calculated_calories = (nutrition["protein"] * 4) + (nutrition["carbs"] * 4) + (nutrition["fat"] * 9)
                if abs(nutrition["calories"] - calculated_calories) > 100:
                    logger.warning(f"Calorie mismatch: estimated {nutrition['calories']}, calculated {calculated_calories}")
                    nutrition["calories"] = calculated_calories
                
                return nutrition
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing nutrition response: {e}")
            logger.error(f"Raw response: {response}")
            return self._fallback_estimation("")
    
    def _fallback_estimation(self, meal_description: str) -> Dict[str, int]:
        """
        Provide fallback nutrition estimation when OpenAI is not available.
        
        Args:
            meal_description: Description of the meal
            
        Returns:
            Dictionary with estimated nutrition values
        """
        # Simple keyword-based estimation
        description_lower = meal_description.lower()
        
        # Base estimates
        calories = 400
        protein = 20
        carbs = 40
        fat = 15
        
        # Adjust based on keywords
        if any(word in description_lower for word in ["chicken", "turkey", "fish", "salmon", "tuna", "beef", "steak", "pork"]):
            protein += 15
            calories += 100
        
        if any(word in description_lower for word in ["rice", "pasta", "bread", "potato", "quinoa", "oatmeal"]):
            carbs += 30
            calories += 120
        
        if any(word in description_lower for word in ["avocado", "nuts", "olive oil", "butter", "cheese"]):
            fat += 10
            calories += 90
        
        if any(word in description_lower for word in ["salad", "vegetables", "greens", "broccoli", "spinach"]):
            calories -= 50
            carbs -= 10
        
        if any(word in description_lower for word in ["fried", "deep fried", "crispy"]):
            fat += 15
            calories += 150
        
        if any(word in description_lower for word in ["grilled", "baked", "roasted"]):
            fat -= 5
            calories -= 50
        
        return {
            "calories": max(200, calories),
            "protein": max(5, protein),
            "carbs": max(10, carbs),
            "fat": max(5, fat)
        }
    
    def estimate_nutrition_batch(self, meal_descriptions: list) -> list:
        """
        Estimate nutrition for multiple meals in batch.
        
        Args:
            meal_descriptions: List of meal descriptions
            
        Returns:
            List of nutrition dictionaries
        """
        results = []
        for description in meal_descriptions:
            nutrition = self.estimate_nutrition(description)
            results.append(nutrition)
        return results
    
    def validate_nutrition_estimate(self, nutrition: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validate a nutrition estimate for reasonableness.
        
        Args:
            nutrition: Dictionary with nutrition values
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        calories = nutrition.get("calories", 0)
        protein = nutrition.get("protein", 0)
        carbs = nutrition.get("carbs", 0)
        fat = nutrition.get("fat", 0)
        
        # Check for reasonable ranges
        if calories < 50 or calories > 2000:
            return False, f"Calories ({calories}) outside reasonable range (50-2000)"
        
        if protein < 0 or protein > 100:
            return False, f"Protein ({protein}g) outside reasonable range (0-100g)"
        
        if carbs < 0 or carbs > 200:
            return False, f"Carbs ({carbs}g) outside reasonable range (0-200g)"
        
        if fat < 0 or fat > 100:
            return False, f"Fat ({fat}g) outside reasonable range (0-100g)"
        
        # Check if calories roughly match macronutrients
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        if abs(calories - calculated_calories) > 200:
            return False, f"Calorie mismatch: {calories} vs calculated {calculated_calories}"
        
        return True, "Valid nutrition estimate"

# Global instance for easy access
nutrition_estimator = NutritionEstimator() 