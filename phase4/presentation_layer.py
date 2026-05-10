"""Presentation Layer: Streamlit-based web UI for restaurant recommendations."""

from typing import Dict, Any, List, Optional
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

from .api_server import RecommendationAPI, RecommendationRequest, UserPreferences


class PresentationLayer:
    """Streamlit-based web interface for restaurant recommendations."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the presentation layer.
        
        Args:
            api_base_url: Base URL for the recommendation API
        """
        self.api_base_url = api_base_url
        self.setup_page_config()
    
    def setup_page_config(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="Restaurant Recommender",
            page_icon="🍽️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def run(self):
        """Run the Streamlit application."""
        st.title("🍽️ AI Restaurant Recommender")
        st.markdown("Get personalized restaurant recommendations powered by AI")
        
        # Sidebar for preferences
        with st.sidebar:
            st.header("Your Preferences")
            user_preferences = self.get_user_preferences()
            
            if st.button("Get Recommendations", type="primary"):
                self.get_and_display_recommendations(user_preferences)
        
        # Main content area
        self.display_main_content()
        
        # Footer
        self.display_footer()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from sidebar inputs."""
        preferences = {}
        
        # Location (required)
        preferences["location"] = st.text_input(
            "Location *",
            placeholder="e.g., Downtown, Koramangala, Indiranagar",
            help="Enter your preferred area or neighborhood"
        )
        
        # Cuisine preferences
        preferences["cuisine"] = st.selectbox(
            "Cuisine Type",
            options=["", "Italian", "Indian", "Chinese", "Japanese", "Mexican", "Thai", "Continental", "American"],
            index=0,
            help="Select your preferred cuisine"
        )
        
        # Budget
        budget_options = ["", "Budget-friendly (≤₹500)", "Moderate (₹500-₹1000)", "Premium (₹1000-₹1500)", "Fine Dining (>₹1500)"]
        budget_selection = st.selectbox("Budget Range", options=budget_options, index=0)
        
        if budget_selection:
            budget_map = {
                "Budget-friendly (≤₹500)": 500,
                "Moderate (₹500-₹1000)": 1000,
                "Premium (₹1000-₹1500)": 1500,
                "Fine Dining (>₹1500)": 2000
            }
            preferences["max_cost_for_two"] = budget_map[budget_selection]
            preferences["budget_category"] = budget_selection.split("(")[0].strip()
        
        # Rating
        preferences["min_rating"] = st.slider(
            "Minimum Rating",
            min_value=1.0,
            max_value=5.0,
            value=3.5,
            step=0.5,
            help="Minimum restaurant rating"
        )
        
        # Meal type
        preferences["meal_type"] = st.selectbox(
            "Meal Type",
            options=["", "Breakfast", "Lunch", "Dinner", "Late Night"],
            index=0
        )
        
        # Occasion
        preferences["occasion"] = st.selectbox(
            "Occasion",
            options=["", "Casual Dining", "Date Night", "Family Meal", "Business Lunch", "Celebration", "Quick Bite"],
            index=0
        )
        
        # Additional requirements
        preferences["additional_requirements"] = st.text_area(
            "Additional Requirements",
            placeholder="e.g., Outdoor seating, Valet parking, Live music, etc.",
            help="Any specific requirements or preferences"
        )
        
        return preferences
    
    def get_and_display_recommendations(self, preferences: Dict[str, Any]):
        """Get recommendations from API and display them."""
        if not preferences.get("location"):
            st.error("Please enter a location to get recommendations")
            return
        
        with st.spinner("Getting AI recommendations..."):
            try:
                # Call API
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
                    result = response.json()
                    self.display_recommendations(result)
                else:
                    st.error(f"Failed to get recommendations: {response.status_code}")
                    st.error(response.text)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
                st.info("Make sure the API server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"Error: {e}")
    
    def display_recommendations(self, result: Dict[str, Any]):
        """Display recommendations in a formatted way."""
        recommendations = result.get("recommendations", [])
        summary = result.get("summary", "")
        response_time = result.get("response_time_ms", 0)
        
        # Summary section
        if summary:
            st.success(summary)
        
        # Response time
        st.caption(f"Generated in {response_time}ms")
        
        if not recommendations:
            st.warning("No recommendations found. Try adjusting your preferences.")
            return
        
        # Display recommendations
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                # Restaurant header
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.subheader(f"{i}. {rec.get('restaurant_name', 'Unknown Restaurant')}")
                
                with col2:
                    if rec.get('match_score'):
                        score = rec.get('match_score', 0) * 100
                        st.metric("Match Score", f"{score:.1f}%")
                
                # Restaurant details
                details_col1, details_col2, details_col3 = st.columns(3)
                
                with details_col1:
                    if rec.get('price_indication'):
                        st.info(f"💰 {rec.get('price_indication')}")
                
                with details_col2:
                    if rec.get('best_for'):
                        st.info(f"🎯 Best for: {rec.get('best_for')}")
                
                with details_col3:
                    # This would come from the original restaurant data
                    st.info("⭐ Rating: 4.2/5")  # Placeholder
                
                # Reasons for recommendation
                if rec.get('reasons'):
                    st.markdown("**Why we recommend this:**")
                    for reason in rec.get('reasons', []):
                        st.markdown(f"• {reason}")
                
                # Highlights
                if rec.get('highlights'):
                    st.markdown("**Highlights:**")
                    highlights_text = ", ".join(rec.get('highlights', []))
                    st.markdown(f"*{highlights_text}*")
                
                st.divider()
    
    def display_main_content(self):
        """Display main content area."""
        # Features section
        st.header("Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.metric("AI-Powered", "Groq LLM")
            st.caption("Fast, intelligent recommendations")
        
        with feature_col2:
            st.metric("Personalized", "Your Taste")
            st.caption("Tailored to your preferences")
        
        with feature_col3:
            st.metric("Instant", "< 1 Second")
            st.caption("Quick response time")
        
        # How it works
        st.header("How It Works")
        
        steps = [
            "📍 Tell us your location and preferences",
            "🤖 Our AI analyzes restaurants matching your criteria", 
            "⭐ Get ranked recommendations with explanations",
            "🍽️ Choose your perfect dining spot"
        ]
        
        for step in steps:
            st.markdown(step)
        
        # Sample recommendations
        if st.checkbox("Show Sample Recommendations"):
            self.display_sample_recommendations()
    
    def display_sample_recommendations(self):
        """Display sample recommendations for demonstration."""
        st.subheader("Sample Recommendations")
        
        sample_data = [
            {
                "restaurant_name": "Bella Italia",
                "match_score": 0.95,
                "price_indication": "Moderate",
                "best_for": "Date Night",
                "reasons": ["Perfect Italian cuisine match", "Excellent rating", "Great ambiance"],
                "highlights": ["Authentic pasta", "Wine selection", "Cozy atmosphere"]
            },
            {
                "restaurant_name": "Spice Garden",
                "match_score": 0.88,
                "price_indication": "Budget-friendly",
                "best_for": "Family Meal",
                "reasons": ["Great value", "Authentic flavors", "Family-friendly"],
                "highlights": ["Traditional recipes", "Vegetarian options", "Quick service"]
            }
        ]
        
        for i, rec in enumerate(sample_data, 1):
            with st.container():
                st.subheader(f"{i}. {rec['restaurant_name']}")
                st.write(f"**Match Score:** {rec['match_score']*100:.1f}%")
                st.write(f"**Price:** {rec['price_indication']}")
                st.write(f"**Best for:** {rec['best_for']}")
                st.write("**Why we recommend:**")
                for reason in rec['reasons']:
                    st.write(f"• {reason}")
                st.write("**Highlights:**")
                st.write(f"*{', '.join(rec['highlights'])}*")
                st.divider()
    
    def display_footer(self):
        """Display footer information."""
        st.markdown("---")
        st.markdown(
            """
            **About:** This restaurant recommender uses AI to provide personalized dining recommendations.
            
            **Powered by:** Groq LLM for fast, intelligent recommendations
            """
        )
        
        # API status
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("🟢 API Status: Online")
            else:
                st.error("🔴 API Status: Error")
        except:
            st.warning("🟡 API Status: Offline")


def create_streamlit_app(api_base_url: str = "http://localhost:8000"):
    """
    Create Streamlit app instance.
    
    Args:
        api_base_url: Base URL for the recommendation API
    """
    app = PresentationLayer(api_base_url)
    app.run()


if __name__ == "__main__":
    # Run the Streamlit app
    create_streamlit_app()
