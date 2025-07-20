# core/goal_matcher.py

from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class GoalMatcher:
    """
    Fuzzy goal matcher for handling natural language input and synonyms.
    
    This class provides fuzzy string matching capabilities to resolve
    user input like 'musle gain' or 'lean bulk' to the correct
    fitness goal identifier.
    """
    
    def __init__(self):
        # Define goal mappings with synonyms and common misspellings
        self.goal_mappings = {
            "muscle_gain": {
                "name": "Muscle Gain",
                "description": "High protein, moderate calories for muscle building",
                "synonyms": [
                    "muscle gain", "musle gain", "muscle building", "musle building",
                    "bulk", "bulking", "lean bulk", "lean bulking", "muscle growth",
                    "musle growth", "gain muscle", "gain musle", "build muscle",
                    "build musle", "muscle development", "musle development",
                    "strength training", "powerlifting", "bodybuilding", "body building",
                    "muscle mass", "musle mass", "gain weight", "put on muscle",
                    "put on musle", "get bigger", "get stronger", "size gains",
                    "muscle hypertrophy", "musle hypertrophy", "mass building",
                    "muscle building", "musle building", "muscle gainer",
                    "musle gainer", "bulk up", "bulkup", "muscle up", "musle up"
                ]
            },
            "weight_loss": {
                "name": "Weight Loss",
                "description": "Lower calories, moderate protein for weight loss",
                "synonyms": [
                    "weight loss", "weightloss", "lose weight", "loose weight",
                    "fat loss", "fatloss", "burn fat", "burning fat", "slim down",
                    "slimdown", "get lean", "getlean", "cut", "cutting", "diet",
                    "dieting", "calorie deficit", "calorie defecit", "weight reduction",
                    "weight reduction", "shed pounds", "shedpounds", "drop weight",
                    "dropweight", "lose fat", "loose fat", "fat burning",
                    "fatburning", "weight management", "weightmanagement",
                    "slimming", "slimming down", "get skinny", "getskinny",
                    "reduce weight", "reduceweight", "lose pounds", "loose pounds"
                ]
            },
            "keto": {
                "name": "Ketogenic Diet",
                "description": "Low carbs, high fat for ketosis",
                "synonyms": [
                    "keto", "ketogenic", "ketogenic diet", "keto diet", "ketodiet",
                    "low carb", "lowcarb", "low carbohydrate", "lowcarbohydrate",
                    "ketosis", "keto diet", "ketogenic diet", "keto lifestyle",
                    "keto lifestyle", "keto eating", "keto eating", "keto plan",
                    "keto plan", "keto meal", "keto meal", "keto food", "keto food",
                    "keto nutrition", "keto nutrition", "keto diet plan",
                    "keto diet plan", "keto meal plan", "keto meal plan",
                    "keto dieting", "keto dieting", "keto eating plan",
                    "keto eating plan", "keto nutrition plan", "keto nutrition plan"
                ]
            },
            "balanced": {
                "name": "Balanced Diet",
                "description": "General healthy eating guidelines",
                "synonyms": [
                    "balanced", "balanced diet", "balanceddiet", "healthy eating",
                    "healthyeating", "healthy diet", "healthydiet", "maintenance",
                    "maintain", "maintaining", "general health", "generalhealth",
                    "overall health", "overallhealth", "wellness", "healthy lifestyle",
                    "healthylifestyle", "balanced nutrition", "balancednutrition",
                    "healthy nutrition", "healthynutrition", "moderate diet",
                    "moderatediet", "sustainable diet", "sustainablediet",
                    "long term health", "longtermhealth", "healthy living",
                    "healthyliving", "balanced eating", "balancedeating",
                    "healthy food", "healthyfood", "nutrition", "good nutrition",
                    "goodnutrition", "proper nutrition", "propernutrition"
                ]
            }
        }
        
        # Create a flat list of all synonyms for fuzzy matching
        self.all_synonyms = []
        for goal_id, goal_info in self.goal_mappings.items():
            self.all_synonyms.extend(goal_info["synonyms"])
    
    def match_goal(self, user_input: str, threshold: int = 80) -> Tuple[Optional[str], int]:
        """
        Match user input to the best fitness goal using fuzzy string matching.
        
        Args:
            user_input: The user's input string (e.g., "musle gain", "lean bulk")
            threshold: Minimum similarity score (0-100) to consider a match
            
        Returns:
            Tuple of (goal_id, confidence_score) or (None, 0) if no match found
        """
        if not user_input or not user_input.strip():
            return None, 0
        
        user_input = user_input.lower().strip()
        
        # First, try exact match with synonyms
        for goal_id, goal_info in self.goal_mappings.items():
            if user_input in goal_info["synonyms"]:
                logger.info(f"Exact match found for '{user_input}' -> {goal_id}")
                return goal_id, 100
        
        # If no exact match, use fuzzy matching
        best_match = process.extractOne(
            user_input, 
            self.all_synonyms,
            scorer=fuzz.token_sort_ratio
        )
        
        if best_match and best_match[1] >= threshold:
            matched_synonym = best_match[0]
            confidence = best_match[1]
            
            # Find which goal this synonym belongs to
            for goal_id, goal_info in self.goal_mappings.items():
                if matched_synonym in goal_info["synonyms"]:
                    logger.info(f"Fuzzy match found for '{user_input}' -> {goal_id} (confidence: {confidence})")
                    return goal_id, confidence
        
        logger.warning(f"No match found for user input: '{user_input}'")
        return None, 0
    
    def get_goal_info(self, goal_id: str) -> Optional[Dict]:
        """
        Get information about a specific goal.
        
        Args:
            goal_id: The goal identifier
            
        Returns:
            Dictionary with goal information or None if not found
        """
        return self.goal_mappings.get(goal_id)
    
    def get_all_goals(self) -> Dict[str, Dict]:
        """
        Get all available goals with their information.
        
        Returns:
            Dictionary of all goals with their information
        """
        return self.goal_mappings
    
    def get_suggestions(self, user_input: str, max_suggestions: int = 3) -> List[Tuple[str, str, int]]:
        """
        Get suggestions for user input that doesn't match any goal.
        
        Args:
            user_input: The user's input string
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of tuples (goal_id, goal_name, confidence_score)
        """
        if not user_input or not user_input.strip():
            return []
        
        user_input = user_input.lower().strip()
        
        # Get all matches with their scores
        matches = process.extract(
            user_input,
            self.all_synonyms,
            scorer=fuzz.token_sort_ratio,
            limit=10
        )
        
        suggestions = []
        seen_goals = set()
        
        for synonym, score in matches:
            # Find which goal this synonym belongs to
            for goal_id, goal_info in self.goal_mappings.items():
                if synonym in goal_info["synonyms"] and goal_id not in seen_goals:
                    suggestions.append((goal_id, goal_info["name"], score))
                    seen_goals.add(goal_id)
                    break
            
            if len(suggestions) >= max_suggestions:
                break
        
        return suggestions

# Global instance for easy access
goal_matcher = GoalMatcher() 