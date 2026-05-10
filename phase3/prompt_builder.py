"""Prompt Builder: Creates and manages prompt templates for LLM recommendations."""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class PromptBuilder:
    """Builds structured prompts for LLM-based restaurant recommendations."""
    
    def __init__(self):
        """Initialize the PromptBuilder with default templates."""
        self.templates = {
            "recommendation": self._get_recommendation_template(),
            "ranking": self._get_ranking_template(),
            "explanation": self._get_explanation_template()
        }
    
    def build_prompt(
        self, 
        context: Dict[str, Any], 
        template_type: str = "recommendation",
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        Build a complete prompt from context and template.
        
        Args:
            context: Structured context from CandidateBuilder
            template_type: Type of prompt template to use
            additional_instructions: Optional custom instructions
            
        Returns:
            Complete prompt string for LLM
        """
        template = self.templates.get(template_type, self.templates["recommendation"])
        
        # Prepare template variables
        variables = {
            "user_preferences": json.dumps(context["user_preferences"], indent=2),
            "candidates": json.dumps(context["candidates"], indent=2),
            "total_candidates": context["total_candidates"],
            "context_summary": context["context_summary"],
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "additional_instructions": additional_instructions or ""
        }
        
        # Fill template
        prompt = template.format(**variables)
        
        return prompt
    
    def _get_recommendation_template(self) -> str:
        """Get the main recommendation prompt template."""
        return """You are a restaurant recommendation expert. Help users find the best dining options based on their preferences.

## User Preferences:
{user_preferences}

## Available Restaurants:
{candidates}

## Task:
Based on the user's preferences and the available restaurants, provide a ranked list of top 5 recommendations with detailed explanations. Focus on:
1. How well each restaurant matches the user's preferences
2. Quality indicators (ratings, popularity)
3. Value for money
4. Unique selling points

## Output Format:
Return a JSON response with this exact structure:
{{
    "recommendations": [
        {{
            "rank": 1,
            "restaurant_name": "Restaurant Name",
            "match_score": 0.95,
            "reasons": [
                "Perfect match for your preference of {preferred_cuisine}",
                "Excellent rating of 4.5+",
                "Great value within your budget"
            ],
            "highlights": [
                "Known for authentic flavors",
                "Popular among locals",
                "Good ambiance"
            ],
            "price_indication": "Budget-friendly/Moderate/Premium",
            "best_for": "Casual dining/Family outings/Date night/etc."
        }}
    ],
    "summary": "Brief summary of recommendations",
    "alternative_suggestions": "If none of these work, consider...",
    "total_matches": {total_candidates}
}}

## Context:
{context_summary}

{additional_instructions}

Please provide thoughtful, personalized recommendations that help the user make an informed decision."""
    
    def _get_ranking_template(self) -> str:
        """Get the ranking-focused prompt template."""
        return """You are a restaurant ranking specialist. Rank the given restaurants based on how well they match user preferences.

## User Preferences:
{user_preferences}

## Restaurants to Rank:
{candidates}

## Ranking Criteria:
- Cuisine match (40% weight)
- Rating quality (25% weight) 
- Price alignment (20% weight)
- Location convenience (15% weight)

## Output Format:
Return JSON with this structure:
{{
    "ranked_restaurants": [
        {{
            "original_rank": 3,
            "new_rank": 1,
            "restaurant_name": "Name",
            "score_breakdown": {{
                "cuisine_match": 0.9,
                "rating": 0.8,
                "price": 0.7,
                "location": 0.8
            }},
            "overall_score": 0.81,
            "ranking_reason": "Why this restaurant moved to this position"
        }}
    ],
    "ranking_methodology": "Brief explanation of ranking approach"
}}

## Context:
{context_summary}

{additional_instructions}"""
    
    def _get_explanation_template(self) -> str:
        """Get the explanation-focused prompt template."""
        return """You are a restaurant critic and advisor. Provide detailed explanations for why these restaurants are recommended.

## User Preferences:
{user_preferences}

## Recommended Restaurants:
{candidates}

## Task:
For each restaurant, provide comprehensive explanations covering:
1. Why it matches the user's specific preferences
2. What makes it special or unique
3. What type of experience to expect
4. Any considerations or tips

## Output Format:
Return JSON with this structure:
{{
    "detailed_explanations": [
        {{
            "rank": 1,
            "restaurant_name": "Name",
            "why_recommended": {
                "preference_match": "Detailed explanation of preference alignment",
                "unique_qualities": "What makes this place special",
                "experience_expectation": "What the user can expect",
                "insider_tips": "Local knowledge or tips"
            },
            "suitability_for": {
                "occasions": ["Date night", "Family dinner", etc.],
                "dietary_considerations": "Vegetarian options, etc.",
                "budget_fit": "How it fits their budget"
            }
        }}
    ]
}}

## Context:
{context_summary}

{additional_instructions}"""
    
    def add_custom_template(self, name: str, template: str) -> None:
        """
        Add a custom prompt template.
        
        Args:
            name: Template name
            template: Template string with {variable} placeholders
        """
        self.templates[name] = template
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def validate_template(self, template: str) -> List[str]:
        """
        Validate template and return list of required variables.
        
        Args:
            template: Template string to validate
            
        Returns:
            List of variable names found in template
        """
        import re
        variables = re.findall(r'\{([^}]+)\}', template)
        return list(set(variables))
    
    def build_system_prompt(self, persona: str = "restaurant expert") -> str:
        """
        Build a system prompt for LLM.
        
        Args:
            persona: Type of persona to adopt
            
        Returns:
            System prompt string
        """
        personas = {
            "restaurant expert": "You are a knowledgeable restaurant recommendation expert with deep understanding of cuisines, dining experiences, and what makes restaurants special.",
            "food critic": "You are an experienced food critic who can identify quality, authenticity, and exceptional dining experiences.",
            "local guide": "You are a local food guide who knows the best hidden gems and popular spots in the area.",
            "budget advisor": "You specialize in finding great value dining options that offer the best experience for the price."
        }
        
        base_prompt = personas.get(persona, personas["restaurant expert"])
        
        system_prompt = f"""{base_prompt}

Your responses should be:
- Helpful and informative
- Honest about limitations or unknown factors
- Focused on the user's specific needs and preferences
- Structured and easy to understand
- Culturally aware and respectful

Always provide responses in the requested JSON format. If you cannot fulfill the request, explain why in the JSON response."""
        
        return system_prompt
    
    def build_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Build few-shot examples for better LLM performance."""
        examples = [
            {
                "input": {
                    "preferences": {"cuisine": "Italian", "budget": 1000, "location": "Downtown"},
                    "candidates": [
                        {"name": "Pasta Paradise", "cuisine": "Italian", "rating": 4.2, "cost": 800}
                    ]
                },
                "output": {
                    "recommendations": [
                        {
                            "rank": 1,
                            "restaurant_name": "Pasta Paradise",
                            "match_score": 0.9,
                            "reasons": ["Perfect Italian cuisine match", "Within budget", "Good rating"]
                        }
                    ]
                }
            }
        ]
        
        return examples
