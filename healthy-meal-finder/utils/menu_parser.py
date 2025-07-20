# utils/menu_parser.py

import logging
import json
import re
from typing import Dict, List, Optional, Tuple
import openai
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MenuParser:
    """
    LLM-powered menu parser using OpenAI GPT-3.5-turbo to extract structured meal data.
    
    This service handles:
    - Parsing raw menu text into structured meal objects
    - Extracting meal names, descriptions, prices, and tags
    - Calculating relevance scores based on fitness goals
    - Fallback parsing when OpenAI is unavailable
    """
    
    def __init__(self):
        self.client = None
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No OpenAI API key found, using fallback parsing")
    
    def parse_menu_text(self, menu_text: str, fitness_goal: str, restaurant_name: str, cuisine: Optional[str] = None, flavor_profile: Optional[str] = None) -> List[Dict]:
        """
        Parse menu text into structured meal objects using LLM.
        
        Args:
            menu_text: Raw menu text from scraping
            fitness_goal: User's fitness goal (muscle_gain, weight_loss, keto, balanced)
            restaurant_name: Name of the restaurant
            cuisine: Preferred cuisine type (optional)
            flavor_profile: Preferred flavor profile (optional)
            
        Returns:
            List of structured meal dictionaries
        """
        if not menu_text or len(menu_text.strip()) < 50:
            logger.warning(f"Menu text too short for {restaurant_name}")
            return []
        
        try:
            if self.client:
                return self._parse_with_openai(menu_text, fitness_goal, restaurant_name, cuisine, flavor_profile)
            else:
                return self._parse_with_fallback(menu_text, fitness_goal, restaurant_name, cuisine, flavor_profile)
        except Exception as e:
            logger.error(f"❌ Failed to parse menu for {restaurant_name}: {e}")
            return self._parse_with_fallback(menu_text, fitness_goal, restaurant_name, cuisine, flavor_profile)
    
    def _parse_with_openai(self, menu_text: str, fitness_goal: str, restaurant_name: str, cuisine: Optional[str] = None, flavor_profile: Optional[str] = None) -> List[Dict]:
        """
        Parse menu using OpenAI GPT-3.5-turbo.
        
        Args:
            menu_text: Raw menu text
            fitness_goal: User's fitness goal
            restaurant_name: Restaurant name
            cuisine: Preferred cuisine type (optional)
            flavor_profile: Preferred flavor profile (optional)
            
        Returns:
            List of structured meal objects
        """
        # Create the prompt for the LLM
        prompt = self._create_parsing_prompt(menu_text, fitness_goal, restaurant_name, cuisine, flavor_profile)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a menu parsing expert. Extract individual meals from menu text and return them as a JSON array."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            meals = self._parse_llm_response(content)
            
            logger.info(f"✅ Successfully parsed {len(meals)} meals from {restaurant_name} using OpenAI")
            return meals
            
        except Exception as e:
            logger.error(f"❌ OpenAI parsing failed for {restaurant_name}: {e}")
            return self._parse_with_fallback(menu_text, fitness_goal, restaurant_name, cuisine, flavor_profile)
    
    def _create_parsing_prompt(self, menu_text: str, fitness_goal: str, restaurant_name: str, cuisine: Optional[str] = None, flavor_profile: Optional[str] = None) -> str:
        """
        Create a detailed prompt for the LLM to parse menu text.
        
        Args:
            menu_text: Raw menu text
            fitness_goal: User's fitness goal
            restaurant_name: Restaurant name
            cuisine: Preferred cuisine type (optional)
            flavor_profile: Preferred flavor profile (optional)
            
        Returns:
            Formatted prompt string
        """
        goal_descriptions = {
            "muscle_gain": "high protein, moderate calories for muscle building",
            "weight_loss": "lower calories, moderate protein for weight loss",
            "keto": "low carbs, high fat for ketosis",
            "balanced": "general healthy eating guidelines"
        }
        
        goal_desc = goal_descriptions.get(fitness_goal, "healthy eating")
        
        # Build preference text
        preferences = []
        if cuisine:
            preferences.append(f"cuisine: {cuisine}")
        if flavor_profile:
            preferences.append(f"flavor profile: {flavor_profile}")
        
        preference_text = ""
        if preferences:
            preference_text = f"\nUser preferences: {', '.join(preferences)}"
        
        prompt = f"""
Parse the following menu text from "{restaurant_name}" and extract individual meals. 
Focus on meals that align with the fitness goal: {fitness_goal} ({goal_desc}).{preference_text}

Menu text:
{menu_text[:3000]}  # Limit to first 3000 chars to avoid token limits

Extract each meal and return as a JSON array with this exact structure:
[
  {{
    "name": "Meal name",
    "description": "Brief description of the meal",
    "price": "Price if available (e.g., '$12.99') or null",
    "tags": ["high protein", "keto", "low carb", "vegetarian", "vegan", "gluten-free"],
    "relevance_score": 0.85  // Score 0-1 based on how well it matches the fitness goal
  }}
]

Guidelines:
- Extract only actual meals/food items, not drinks or desserts unless they're healthy
- For muscle_gain: prioritize high protein items (chicken, fish, lean meats)
- For weight_loss: prioritize lower calorie items
- For keto: prioritize low carb, high fat items
- For balanced: include a variety of healthy options
- If cuisine preference is specified, prioritize meals from that cuisine type
- If flavor profile is specified, prioritize meals with that flavor characteristic
- Relevance score: 0.0-1.0 based on how well the meal fits the goal and preferences
- Tags should reflect dietary characteristics (high protein, low carb, etc.)
- Price should be extracted if visible, otherwise null
- Return maximum 10 meals, prioritize the most relevant ones

Return only valid JSON, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """
        Parse the LLM response into structured meal objects.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            List of meal dictionaries
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                meals = json.loads(json_str)
                
                # Validate and clean meals
                validated_meals = []
                for meal in meals:
                    if self._validate_meal(meal):
                        validated_meals.append(self._clean_meal(meal))
                
                return validated_meals
            else:
                logger.warning("No JSON array found in LLM response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []
    
    def _parse_with_fallback(self, menu_text: str, fitness_goal: str, restaurant_name: str, cuisine: Optional[str] = None, flavor_profile: Optional[str] = None) -> List[Dict]:
        """
        Fallback parsing when OpenAI is unavailable.
        
        Args:
            menu_text: Raw menu text
            fitness_goal: User's fitness goal
            restaurant_name: Restaurant name
            cuisine: Preferred cuisine type (optional)
            flavor_profile: Preferred flavor profile (optional)
            
        Returns:
            List of structured meal objects
        """
        logger.info(f"Using fallback parsing for {restaurant_name}")
        
        # Simple keyword-based parsing
        meals = []
        lines = menu_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Look for meal-like patterns
            if self._is_meal_line(line):
                meal = self._extract_meal_from_line(line, fitness_goal)
                if meal:
                    meals.append(meal)
        
        # Limit to top 5 meals
        meals = sorted(meals, key=lambda x: x['relevance_score'], reverse=True)[:5]
        
        logger.info(f"Fallback parsing found {len(meals)} meals for {restaurant_name}")
        return meals
    
    def _is_meal_line(self, line: str) -> bool:
        """
        Determine if a line contains meal information.
        
        Args:
            line: Text line to analyze
            
        Returns:
            True if line appears to be a meal
        """
        # Meal indicators
        meal_keywords = [
            'chicken', 'beef', 'salmon', 'pasta', 'salad', 'soup', 'burger',
            'pizza', 'steak', 'fish', 'vegetable', 'rice', 'quinoa', 'tofu',
            'bowl', 'wrap', 'sandwich', 'entree', 'main', 'dish'
        ]
        
        # Price pattern
        price_pattern = r'\$[\d,]+\.?\d*'
        
        line_lower = line.lower()
        has_meal_keyword = any(keyword in line_lower for keyword in meal_keywords)
        has_price = bool(re.search(price_pattern, line))
        has_length = len(line) > 10
        
        return has_meal_keyword or (has_price and has_length)
    
    def _extract_meal_from_line(self, line: str, fitness_goal: str) -> Optional[Dict]:
        """
        Extract meal information from a single line.
        
        Args:
            line: Text line containing meal info
            fitness_goal: User's fitness goal
            
        Returns:
            Meal dictionary or None
        """
        # Extract price
        price_match = re.search(r'\$[\d,]+\.?\d*', line)
        price = price_match.group(0) if price_match else None
        
        # Extract meal name (everything before price or first 50 chars)
        if price:
            name = line.split(price)[0].strip()
        else:
            name = line[:50].strip()
        
        # Generate description
        description = line.replace(price, '').strip() if price else line
        
        # Determine tags based on content
        tags = self._extract_tags(line)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(line, fitness_goal)
        
        return {
            "name": name,
            "description": description,
            "price": price,
            "tags": tags,
            "relevance_score": relevance_score
        }
    
    def _extract_tags(self, text: str) -> List[str]:
        """
        Extract dietary tags from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dietary tags
        """
        tags = []
        text_lower = text.lower()
        
        # Protein tags
        if any(word in text_lower for word in ['chicken', 'beef', 'steak', 'fish', 'salmon', 'tuna']):
            tags.append("high protein")
        
        # Carb tags
        if any(word in text_lower for word in ['pasta', 'rice', 'bread', 'potato']):
            tags.append("high carb")
        elif any(word in text_lower for word in ['salad', 'vegetable', 'quinoa']):
            tags.append("low carb")
        
        # Dietary restrictions
        if any(word in text_lower for word in ['vegetarian', 'veggie']):
            tags.append("vegetarian")
        if any(word in text_lower for word in ['vegan']):
            tags.append("vegan")
        if any(word in text_lower for word in ['gluten']):
            tags.append("gluten-free")
        
        # Keto-friendly
        if any(word in text_lower for word in ['avocado', 'olive', 'cheese', 'butter']):
            tags.append("keto")
        
        return tags
    
    def _calculate_relevance_score(self, text: str, fitness_goal: str) -> float:
        """
        Calculate relevance score based on fitness goal.
        
        Args:
            text: Meal text
            fitness_goal: User's fitness goal
            
        Returns:
            Relevance score (0.0-1.0)
        """
        text_lower = text.lower()
        score = 0.5  # Base score
        
        if fitness_goal == "muscle_gain":
            # High protein foods
            protein_keywords = ['chicken', 'beef', 'steak', 'fish', 'salmon', 'tuna', 'protein']
            protein_count = sum(1 for keyword in protein_keywords if keyword in text_lower)
            score += min(protein_count * 0.2, 0.4)
            
        elif fitness_goal == "weight_loss":
            # Low calorie foods
            low_cal_keywords = ['salad', 'vegetable', 'soup', 'light', 'grilled']
            low_cal_count = sum(1 for keyword in low_cal_keywords if keyword in text_lower)
            score += min(low_cal_count * 0.15, 0.4)
            
        elif fitness_goal == "keto":
            # Low carb, high fat foods
            keto_keywords = ['avocado', 'olive', 'cheese', 'butter', 'fat', 'keto']
            keto_count = sum(1 for keyword in keto_keywords if keyword in text_lower)
            score += min(keto_count * 0.2, 0.4)
            
        else:  # balanced
            # Healthy foods
            healthy_keywords = ['grilled', 'baked', 'fresh', 'organic', 'vegetable']
            healthy_count = sum(1 for keyword in healthy_keywords if keyword in text_lower)
            score += min(healthy_count * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _validate_meal(self, meal: Dict) -> bool:
        """
        Validate a meal object has required fields.
        
        Args:
            meal: Meal dictionary to validate
            
        Returns:
            True if meal is valid
        """
        required_fields = ['name', 'description', 'tags', 'relevance_score']
        return all(field in meal for field in required_fields)
    
    def _clean_meal(self, meal: Dict) -> Dict:
        """
        Clean and normalize a meal object.
        
        Args:
            meal: Meal dictionary to clean
            
        Returns:
            Cleaned meal dictionary
        """
        # Ensure all required fields exist
        cleaned = {
            "name": meal.get("name", "").strip(),
            "description": meal.get("description", "").strip(),
            "price": meal.get("price"),
            "tags": meal.get("tags", []),
            "relevance_score": float(meal.get("relevance_score", 0.5))
        }
        
        # Clean price
        if cleaned["price"]:
            cleaned["price"] = cleaned["price"].strip()
        
        # Ensure tags is a list
        if not isinstance(cleaned["tags"], list):
            cleaned["tags"] = []
        
        # Ensure relevance score is between 0 and 1
        cleaned["relevance_score"] = max(0.0, min(1.0, cleaned["relevance_score"]))
        
        return cleaned

# Global parser instance
menu_parser = MenuParser() 