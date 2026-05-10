"""Simple live test script for Phase 4 with Bellandur example."""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase4.groq_provider import GroqProvider, create_groq_config
from phase4.app_orchestrator import create_phase4_app


def load_sample_restaurant_data():
    """Create sample restaurant data for testing."""
    return [
        {
            "name": "The Bellandur Bistro",
            "cuisine": "Continental",
            "rating": 4.2,
            "cost_for_two": 1200,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Rooftop seating", "Live music", "Craft cocktails"]
        },
        {
            "name": "Spice Garden Bellandur",
            "cuisine": "Indian",
            "rating": 4.5,
            "cost_for_two": 800,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Authentic North Indian", "Family friendly", "Buffet available"]
        },
        {
            "name": "Pasta Paradise",
            "cuisine": "Italian",
            "rating": 4.1,
            "cost_for_two": 1000,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": False,
            "highlights": ["Wood-fired pizza", "Fresh pasta", "Wine selection"]
        },
        {
            "name": "Sakura Japanese Cuisine",
            "cuisine": "Japanese",
            "rating": 4.6,
            "cost_for_two": 1800,
            "location": "Bellandur",
            "delivery": False,
            "takeaway": True,
            "highlights": ["Sushi bar", "Teppanyaki", "Authentic flavors"]
        },
        {
            "name": "The Tandoor House",
            "cuisine": "Indian",
            "rating": 4.3,
            "cost_for_two": 900,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Tandoor specialties", "Mughlai cuisine", "Outdoor seating"]
        },
        {
            "name": "Brew & Bite",
            "cuisine": "Continental",
            "rating": 4.0,
            "cost_for_two": 1500,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": False,
            "highlights": ["Craft beer", "Pub atmosphere", "Sports screenings"]
        },
        {
            "name": "Dragon Palace",
            "cuisine": "Chinese",
            "rating": 4.4,
            "cost_for_two": 1100,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": True,
            "highlights": ["Sichuan cuisine", "Dim sum", "Family restaurant"]
        },
        {
            "name": "Bellandur Kitchen",
            "cuisine": "Multi-cuisine",
            "rating": 3.9,
            "cost_for_two": 700,
            "location": "Bellandur",
            "delivery": True,
            "takeaway": True,
            "highlights": ["24/7 service", "Quick service", "Value for money"]
        }
    ]


def get_groq_api_key():
    """Get Groq API key from environment or file."""
    # Try environment variable first
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key
    
    # Try reading from .env file
    try:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("GROQ_API_KEY="):
                        return line.split("=", 1)[1].strip()
    except Exception:
        pass
    
    return None


def test_groq_connection():
    """Test Groq API connection."""
    print("=" * 60)
    print("🔗 TESTING GROQ API CONNECTION")
    print("=" * 60)
    
    # Get API key
    groq_api_key = get_groq_api_key()
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found")
        print("Please set GROQ_API_KEY environment variable or add to .env file")
        return False
    
    print(f"✅ API key found: {groq_api_key[:10]}...{groq_api_key[-10:]}")
    
    try:
        # Create Groq config
        config = create_groq_config(
            api_key=groq_api_key,
            model_name="llama3-8b-8192",
            temperature=0.7
        )
        
        # Create provider
        provider = GroqProvider(config)
        
        print(f"🤖 Using model: {config.model_name}")
        
        # Test connection
        print("🔄 Testing connection...")
        if provider.test_connection():
            print("✅ Groq connection successful!")
        else:
            print("❌ Groq connection failed")
            return False
        
        # Test simple generation
        print("🔄 Testing simple generation...")
        test_prompt = "List 3 popular restaurant cuisines in Bangalore."
        test_response = provider.generate_response(test_prompt)
        print(f"✅ Test response: {test_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        return False


def test_phase4_complete_pipeline():
    """Test complete Phase 4 pipeline with Bellandur example."""
    print("\n" + "=" * 60)
    print("🍽️  TESTING PHASE 4 COMPLETE PIPELINE")
    print("=" * 60)
    
    # Get API key
    groq_api_key = get_groq_api_key()
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found")
        return False
    
    try:
        # Create Phase 4 app
        print("🔄 Initializing Phase 4 app...")
        app = create_phase4_app(groq_api_key)
        
        # Override with sample data for testing
        app.restaurants_data = load_sample_restaurant_data()
        print(f"✅ Loaded {len(app.restaurants_data)} sample restaurants")
        
        # Test preferences (Bellandur, Budget 2000, Rating 4.0)
        test_preferences = {
            "location": "Bellandur",
            "max_cost_for_two": 2000,
            "min_rating": 4.0,
            "cuisine": None,  # No specific cuisine preference
            "occasion": "casual dining"
        }
        
        print(f"\n📋 TEST INPUT:")
        print(f"   Location: {test_preferences['location']}")
        print(f"   Budget: ₹{test_preferences['max_cost_for_two']} for two")
        print(f"   Min Rating: {test_preferences['min_rating']}/5.0")
        print(f"   Occasion: {test_preferences['occasion']}")
        
        # Generate recommendations
        print("\n🔄 Generating AI recommendations...")
        start_time = datetime.now()
        
        result = app.generate_recommendations_complete(
            test_preferences,
            response_type="recommendation",
            max_recommendations=5
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"✅ Recommendations generated in {response_time:.0f}ms")
        
        # Display results
        display_recommendations(result, test_preferences)
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 4 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_recommendations(result, preferences):
    """Display recommendations in a formatted way."""
    print("\n" + "=" * 60)
    print("📊 AI RECOMMENDATION RESULTS")
    print("=" * 60)
    
    recommendations = result.get("recommendations", [])
    summary = result.get("summary", "")
    metadata = result.get("pipeline_metadata", {})
    
    # Summary
    if summary:
        print(f"📝 {summary}")
    
    # Stats
    print(f"\n📈 Statistics:")
    print(f"   • Total candidates found: {metadata.get('total_candidates', 0)}")
    print(f"   • Candidates used: {metadata.get('candidates_used', 0)}")
    print(f"   • Response time: {metadata.get('response_time_ms', 0)}ms")
    print(f"   • LLM Model: {metadata.get('groq_model', 'N/A')}")
    
    # Recommendations
    if not recommendations:
        print("\n❌ No recommendations found")
        return
    
    print(f"\n🍽️  TOP {len(recommendations)} RESTAURANT RECOMMENDATIONS:")
    print("-" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. 📍 {rec.get('restaurant_name', 'Unknown Restaurant')}")
        
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
        
        print("-" * 40)
    
    # Fallback info
    if result.get("fallback_used"):
        print(f"\n⚠️  Fallback mode used: {result.get('fallback_reason', 'N/A')}")


def main():
    """Main test function."""
    print("🚀 PHASE 4 LIVE TEST - BELLANDUR EXAMPLE")
    print("=" * 60)
    print("Testing with: Location=Bellandur, Budget=₹2000, Rating=4.0")
    print("=" * 60)
    
    # Test 1: Groq connection
    if not test_groq_connection():
        print("\n❌ Groq connection test failed. Cannot proceed with Phase 4 test.")
        return
    
    # Test 2: Complete Phase 4 pipeline
    if test_phase4_complete_pipeline():
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("Phase 4 is working correctly with Groq LLM integration.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED!")
        print("Please check the error messages above.")
        print("=" * 60)


if __name__ == "__main__":
    main()
