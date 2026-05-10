"""Example usage script for Phase 3 LLM-based recommendations."""

import os
import logging
from typing import Dict, Any, List

from .pipeline import Phase3Pipeline, Phase3Config, create_default_config
from .llm_client import LLMConfig


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_sample_candidates() -> List[Dict[str, Any]]:
    """Get sample restaurant candidates for testing."""
    return [
        {
            "name": "Bella Italia",
            "cuisine": "Italian",
            "rating": 4.5,
            "cost_for_two": 800,
            "location": "Downtown",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Authentic pasta", "Cozy ambiance"]
        },
        {
            "name": "Spice Route",
            "cuisine": "Indian",
            "rating": 4.2,
            "cost_for_two": 600,
            "location": "Downtown",
            "delivery": False,
            "takeaway": True,
            "highlights": ["Traditional curries", "Vegetarian friendly"]
        },
        {
            "name": "Sakura Sushi",
            "cuisine": "Japanese",
            "rating": 4.8,
            "cost_for_two": 1200,
            "location": "Downtown",
            "delivery": True,
            "takeaway": False,
            "highlights": ["Fresh fish", "Omakase available"]
        },
        {
            "name": "Taco Fiesta",
            "cuisine": "Mexican",
            "rating": 4.0,
            "cost_for_two": 500,
            "location": "Downtown",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Authentic tacos", "Great margaritas"]
        },
        {
            "name": "Le Petit Bistro",
            "cuisine": "French",
            "rating": 4.6,
            "cost_for_two": 1500,
            "location": "Downtown",
            "delivery": False,
            "takeaway": False,
            "highlights": ["Fine dining", "Wine selection"]
        }
    ]


def get_sample_preferences() -> Dict[str, Any]:
    """Get sample user preferences for testing."""
    return {
        "location": "Downtown",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "max_cost_for_two": 1000,
        "budget_category": "moderate",
        "preferred_cuisines": ["Italian", "Continental"],
        "meal_type": "dinner",
        "occasion": "date night"
    }


def example_basic_recommendations():
    """Example of basic recommendation generation."""
    print("=== Basic Recommendations Example ===\n")
    
    # Create configuration (using local provider for demo)
    config = create_default_config(
        provider="local",
        model_name="llama2",
        api_base="http://localhost:11434"
    )
    
    # Initialize pipeline
    pipeline = Phase3Pipeline(config)
    
    # Get sample data
    candidates = get_sample_candidates()
    preferences = get_sample_preferences()
    
    print(f"User Preferences: {preferences}")
    print(f"Found {len(candidates)} candidates\n")
    
    try:
        # Generate recommendations
        result = pipeline.generate_recommendations(candidates, preferences)
        
        # Display results
        print("Generated Recommendations:")
        print(pipeline.format_for_display(result))
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure you have a local LLM server running or configure API keys")


def example_ranking_analysis():
    """Example of ranking-focused analysis."""
    print("\n=== Ranking Analysis Example ===\n")
    
    # Create configuration
    config = create_default_config(
        provider="local",
        model_name="llama2",
        prompt_template="ranking"
    )
    
    pipeline = Phase3Pipeline(config)
    
    candidates = get_sample_candidates()
    preferences = get_sample_preferences()
    
    try:
        # Generate ranking
        result = pipeline.generate_ranking(candidates, preferences)
        
        print("Ranking Analysis:")
        print(pipeline.format_for_display(result))
        
    except Exception as e:
        print(f"Error: {e}")


def example_detailed_explanations():
    """Example of detailed explanations."""
    print("\n=== Detailed Explanations Example ===\n")
    
    # Create configuration
    config = create_default_config(
        provider="local",
        model_name="llama2",
        prompt_template="explanation"
    )
    
    pipeline = Phase3Pipeline(config)
    
    candidates = get_sample_candidates()
    preferences = get_sample_preferences()
    
    try:
        # Generate explanations
        result = pipeline.generate_explanations(candidates, preferences)
        
        print("Detailed Explanations:")
        print(pipeline.format_for_display(result))
        
    except Exception as e:
        print(f"Error: {e}")


def example_pipeline_testing():
    """Example of pipeline testing."""
    print("\n=== Pipeline Testing Example ===\n")
    
    # Create configuration
    config = create_default_config(
        provider="local",
        model_name="llama2"
    )
    
    pipeline = Phase3Pipeline(config)
    
    # Test pipeline
    candidates = get_sample_candidates()
    preferences = get_sample_preferences()
    
    test_passed = pipeline.test_pipeline(candidates, preferences)
    print(f"Pipeline test passed: {test_passed}")
    
    # Show pipeline info
    print("\nPipeline Info:")
    info = pipeline.get_pipeline_info()
    for key, value in info.items():
        print(f"{key}: {value}")


def example_with_openai():
    """Example using OpenAI API (requires API key)."""
    print("\n=== OpenAI API Example ===\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Set OPENAI_API_KEY environment variable to run this example.")
        return
    
    # Create OpenAI configuration
    config = create_default_config(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key=api_key,
        max_tokens=1500,
        temperature=0.7
    )
    
    pipeline = Phase3Pipeline(config)
    
    candidates = get_sample_candidates()
    preferences = get_sample_preferences()
    
    try:
        # Generate recommendations
        result = pipeline.generate_recommendations(
            candidates, 
            preferences,
            additional_instructions="Focus on romantic atmosphere for a date night"
        )
        
        print("OpenAI Recommendations:")
        print(pipeline.format_for_display(result))
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function to run examples."""
    setup_logging()
    
    print("Phase 3 LLM Recommendation System Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_recommendations()
    example_ranking_analysis()
    example_detailed_explanations()
    example_pipeline_testing()
    example_with_openai()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
