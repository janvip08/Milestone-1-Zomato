"""CLI Interface: Command-line interface for restaurant recommendations."""

from typing import Dict, Any, List, Optional
import argparse
import json
import sys
from datetime import datetime
import requests

from .api_server import RecommendationAPI, RecommendationRequest, UserPreferences


class CLIInterface:
    """Command-line interface for restaurant recommendations."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the CLI interface.
        
        Args:
            api_base_url: Base URL for the recommendation API
        """
        self.api_base_url = api_base_url
    
    def run_interactive(self):
        """Run interactive CLI mode."""
        print("🍽️  AI Restaurant Recommender - CLI Mode")
        print("=" * 50)
        print("Get personalized restaurant recommendations from the command line.")
        print()
        
        while True:
            try:
                # Get user preferences
                preferences = self.get_preferences_interactive()
                
                if not preferences:
                    print("No preferences provided. Exiting.")
                    break
                
                # Get recommendations
                recommendations = self.get_recommendations(preferences)
                
                # Display results
                self.display_recommendations(recommendations)
                
                # Ask if user wants to continue
                print()
                continue_choice = input("Get more recommendations? (y/n): ").lower()
                if continue_choice != 'y':
                    print("Thank you for using AI Restaurant Recommender!")
                    break
                    
                print("\n" + "=" * 50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again or contact support if the issue persists.")
    
    def get_preferences_interactive(self) -> Optional[Dict[str, Any]]:
        """Get user preferences interactively."""
        preferences = {}
        
        print("Please enter your preferences (press Enter to use defaults):")
        print()
        
        # Location (required)
        while True:
            location = input("Location (required): ").strip()
            if location:
                preferences["location"] = location
                break
            else:
                print("Location is required. Please enter a location.")
        
        # Cuisine
        cuisine_options = ["", "Italian", "Indian", "Chinese", "Japanese", "Mexican", "Thai", "Continental", "American"]
        print("\nAvailable cuisines:", ", ".join(cuisine_options[1:]))
        cuisine = input("Cuisine (optional): ").strip()
        if cuisine and cuisine in cuisine_options:
            preferences["cuisine"] = cuisine
        
        # Budget
        budget_options = ["", "500", "1000", "1500", "2000"]
        print("\nBudget options for two people:")
        print("1. Budget-friendly (≤₹500)")
        print("2. Moderate (≤₹1000)")
        print("3. Premium (≤₹1500)")
        print("4. Fine Dining (≤₹2000)")
        
        budget_choice = input("Select budget (1-4, optional): ").strip()
        if budget_choice in ["1", "2", "3", "4"]:
            preferences["max_cost_for_two"] = int(budget_options[int(budget_choice)])
        
        # Rating
        rating_input = input("Minimum rating (1.0-5.0, default 3.5): ").strip()
        try:
            rating = float(rating_input) if rating_input else 3.5
            if 1.0 <= rating <= 5.0:
                preferences["min_rating"] = rating
        except ValueError:
            print("Invalid rating. Using default 3.5")
            preferences["min_rating"] = 3.5
        
        # Meal type
        meal_options = ["", "Breakfast", "Lunch", "Dinner", "Late Night"]
        print(f"\nMeal types: {', '.join(meal_options[1:])}")
        meal_type = input("Meal type (optional): ").strip()
        if meal_type and meal_type in meal_options:
            preferences["meal_type"] = meal_type
        
        # Occasion
        occasion_options = ["", "Casual Dining", "Date Night", "Family Meal", "Business Lunch", "Celebration"]
        print(f"\nOccasions: {', '.join(occasion_options[1:])}")
        occasion = input("Occasion (optional): ").strip()
        if occasion and occasion in occasion_options:
            preferences["occasion"] = occasion
        
        # Additional requirements
        additional = input("Additional requirements (optional): ").strip()
        if additional:
            preferences["additional_requirements"] = additional
        
        return preferences
    
    def get_recommendations(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations from API."""
        print("\n🤖 Getting AI recommendations...")
        
        try:
            response = requests.post(
                f"{self.api_base_url}/recommend",
                json={
                    "preferences": preferences,
                    "max_recommendations": 5,
                    "response_type": "recommendation",
                    "include_explanations": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                raise Exception(f"API Error ({response.status_code}): {error_data.get('detail', response.text)}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to API server. Make sure the server is running on http://localhost:8000")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again.")
        except Exception as e:
            raise Exception(f"Failed to get recommendations: {e}")
    
    def display_recommendations(self, result: Dict[str, Any]):
        """Display recommendations in CLI format."""
        recommendations = result.get("recommendations", [])
        summary = result.get("summary", "")
        response_time = result.get("response_time_ms", 0)
        total_matches = result.get("total_matches", 0)
        
        print("\n" + "=" * 50)
        print("📋 RECOMMENDATIONS")
        print("=" * 50)
        
        # Summary
        if summary:
            print(f"📝 {summary}")
        
        # Stats
        print(f"📊 Found {total_matches} restaurants, showing top {len(recommendations)}")
        print(f"⚡ Generated in {response_time}ms")
        print()
        
        if not recommendations:
            print("❌ No recommendations found.")
            return
        
        # Display each recommendation
        for i, rec in enumerate(recommendations, 1):
            print(f"🍽️  {i}. {rec.get('restaurant_name', 'Unknown Restaurant')}")
            
            # Score and basic info
            score = rec.get('match_score', 0) * 100
            print(f"   📊 Match Score: {score:.1f}%")
            
            if rec.get('price_indication'):
                print(f"   💰 Price: {rec['price_indication']}")
            
            if rec.get('best_for'):
                print(f"   🎯 Best for: {rec['best_for']}")
            
            # Reasons
            if rec.get('reasons'):
                print("   ✅ Why we recommend:")
                for reason in rec.get('reasons', []):
                    print(f"      • {reason}")
            
            # Highlights
            if rec.get('highlights'):
                print("   ⭐ Highlights:")
                for highlight in rec.get('highlights', []):
                    print(f"      • {highlight}")
            
            print()
    
    def run_single_command(self, args):
        """Run single command with arguments."""
        preferences = {}
        
        # Parse arguments
        if args.location:
            preferences["location"] = args.location
        else:
            print("Error: Location is required")
            sys.exit(1)
        
        if args.cuisine:
            preferences["cuisine"] = args.cuisine
        
        if args.max_cost:
            preferences["max_cost_for_two"] = args.max_cost
        
        if args.min_rating:
            preferences["min_rating"] = args.min_rating
        
        if args.meal_type:
            preferences["meal_type"] = args.meal_type
        
        if args.occasion:
            preferences["occasion"] = args.occasion
        
        if args.additional:
            preferences["additional_requirements"] = args.additional
        
        # Get recommendations
        try:
            recommendations = self.get_recommendations(preferences)
            
            # Output format
            if args.output == "json":
                print(json.dumps(recommendations, indent=2))
            else:
                self.display_recommendations(recommendations)
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def check_api_status(self):
        """Check API server status."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ API Status: Online")
                print(f"   Groq Connection: {'✅' if data.get('groq_connection') else '❌'}")
                print(f"   Restaurants Loaded: {data.get('restaurants_loaded', 0)}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            else:
                print(f"❌ API Status: Error ({response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ API Status: Offline (Cannot connect)")
        except Exception as e:
            print(f"❌ API Status: Error - {e}")


def create_cli_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="AI Restaurant Recommender CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m phase4.cli_interface
  
  # Single command
  python -m phase4.cli_interface --location "Downtown" --cuisine "Italian"
  
  # With budget and rating
  python -m phase4.cli_interface --location "Koramangala" --max-cost 1000 --min-rating 4.0
  
  # JSON output
  python -m phase4.cli_interface --location "Downtown" --output json
        """
    )
    
    # Interactive mode flag
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (default if no arguments provided)"
    )
    
    # Preference arguments
    parser.add_argument("--location", help="Location (required)")
    parser.add_argument("--cuisine", help="Cuisine type")
    parser.add_argument("--max-cost", type=int, help="Maximum cost for two")
    parser.add_argument("--min-rating", type=float, help="Minimum rating (1.0-5.0)")
    parser.add_argument("--meal-type", help="Meal type")
    parser.add_argument("--occasion", help="Occasion")
    parser.add_argument("--additional", help="Additional requirements")
    
    # Output options
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    # API options
    parser.add_argument("--api-url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--status", action="store_true", help="Check API server status")
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Create CLI interface
    cli = CLIInterface(args.api_url)
    
    # Handle status check
    if args.status:
        cli.check_api_status()
        return
    
    # Determine mode
    if len(sys.argv) == 1 or args.interactive:
        # Interactive mode
        cli.run_interactive()
    else:
        # Single command mode
        cli.run_single_command(args)


if __name__ == "__main__":
    main()
