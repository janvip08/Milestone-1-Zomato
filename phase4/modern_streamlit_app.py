"""
Modern Streamlit Restaurant Recommendation App
Production-ready UI matching modern dark theme design
"""

import os
import sys
import streamlit as st
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernRestaurantApp:
    """Modern Streamlit app with dark theme and proper UX"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize modern Streamlit app.
        
        Args:
            api_base_url: Base URL for the recommendation API
        """
        self.api_base_url = api_base_url
        self.setup_page_config()
        self.setup_custom_css()
    
    def setup_page_config(self):
        """Setup modern page configuration."""
        st.set_page_config(
            page_title="🍽 AI Restaurant Finder",
            page_icon="🍽️",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': "https://github.com/janvip08/Milestone-1-Zomato/issues",
                'About': None
            }
        )
    
    def setup_custom_css(self):
        """Setup modern dark theme CSS matching reference design."""
        st.markdown("""
        <style>
        /* Dark theme and modern design */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
        }
        
        .main .block-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem 2.5rem;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Sidebar styling */
        .css-1lrlq3 {
            background: rgba(255, 255, 255, 0.02);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            color: #ffffff;
            font-size: 14px;
        }
        
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            color: #ffffff;
            font-size: 14px;
        }
        
        .stSlider > div > div > div {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            color: #ffffff;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Card styling */
        .recommendation-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .recommendation-card:hover {
            background: rgba(255, 255, 255, 0.12);
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }
        
        /* Metric styling */
        .stMetric {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Header styling */
        .app-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem 0;
        }
        
        .app-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: transparent;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            display: inline-block;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem 1.5rem;
                margin-top: 0.5rem;
            }
            
            .stButton > button {
                padding: 10px 20px;
                font-size: 13px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from modern sidebar inputs."""
        preferences = {}
        
        with st.sidebar:
            st.markdown("### 🎯 Your Preferences")
            st.markdown("---")
            
            # Location input with search
            preferences["location"] = st.text_input(
                "📍 Location *",
                placeholder="e.g., Koramangala, Indiranagar, Whitefield",
                help="Enter your preferred area or neighborhood"
            )
            
            # Cuisine dropdown
            cuisine_options = ["", "Italian", "Indian", "Chinese", "Japanese", "Mexican", "Thai", "Continental", "American"]
            preferences["cuisine"] = st.selectbox(
                "🍽 Cuisine Type",
                options=cuisine_options,
                index=0,
                help="Select your preferred cuisine"
            )
            
            # Budget input
            budget_options = ["", "Budget-friendly (≤₹500)", "Moderate (₹500-₹1000)", "Premium (₹1000-₹1500)", "Fine Dining (>₹1500)"]
            budget_selection = st.selectbox("💰 Budget Range", options=budget_options, index=0)
            
            if budget_selection:
                budget_map = {
                    "Budget-friendly (≤₹500)": 500,
                    "Moderate (₹500-₹1000)": 1000,
                    "Premium (₹1000-₹1500)": 1500,
                    "Fine Dining (>₹1500)": 2000
                }
                preferences["max_cost_for_two"] = budget_map[budget_selection]
                preferences["budget_category"] = budget_selection.split("(")[0].strip()
            
            # Rating slider
            preferences["min_rating"] = st.slider(
                "⭐ Minimum Rating",
                min_value=1.0,
                max_value=5.0,
                value=4.0,
                step=0.5,
                help="Minimum restaurant rating"
            )
            
            # Max recommendations slider
            preferences["max_recommendations"] = st.slider(
                "🔢 Max Recommendations",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
                help="Maximum number of recommendations to show"
            )
            
            # Additional requirements
            preferences["additional_requirements"] = st.text_area(
                "📝 Additional Requirements",
                placeholder="e.g., Outdoor seating, Valet parking, Live music, etc.",
                help="Any specific requirements or preferences"
            )
        
        return preferences
    
    def get_and_display_recommendations(self, preferences: Dict[str, Any]):
        """Get recommendations from API and display them with modern UI."""
        if not preferences.get("location"):
            st.error("📍 Please enter a location to get recommendations")
            return
        
        # Show preferences summary
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.metric("📍 Location", preferences.get("location", "Not set"))
            with col2:
                st.metric("🍽 Cuisine", preferences.get("cuisine", "Any"))
            with col3:
                st.metric("💰 Budget", preferences.get("budget_category", "Any"))
        
        with st.spinner("🤖 Getting AI recommendations..."):
            try:
                # Call API with proper error handling
                request_data = {
                    "preferences": preferences,
                    "max_recommendations": preferences.get("max_recommendations", 5),
                    "response_type": "recommendation",
                    "include_explanations": True
                }
                
                response = requests.post(
                    f"{self.api_base_url}/recommend",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.display_modern_recommendations(result)
                else:
                    st.error(f"❌ Failed to get recommendations: {response.status_code}")
                    st.error(f"📝 Response: {response.text}")
                    st.info("🔧 Check that the API server is running on http://localhost:8000")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Connection error: {e}")
                st.info("🔧 Make sure the API server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
    
    def display_modern_recommendations(self, result: Dict[str, Any]):
        """Display recommendations with modern card design."""
        recommendations = result.get("recommendations", [])
        summary = result.get("summary", "")
        response_time = result.get("response_time_ms", 0)
        
        if not recommendations:
            st.warning("🔍 No recommendations found. Try adjusting your preferences.")
            return
        
        # Success message with response time
        st.success(f"✅ Found {len(recommendations)} recommendations in {response_time}ms")
        
        # Display recommendations in modern cards
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                # Restaurant card header
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #667eea; font-size: 1.2rem;">
                            {i}. {rec.get('restaurant_name', 'Unknown Restaurant')}
                        </h3>
                        {self._get_rating_stars(rec.get('rating', 0))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Restaurant details
                details_col1, details_col2 = st.columns(2)
                
                with details_col1:
                    if rec.get('cost_indication'):
                        st.markdown(f"**💰 {rec.get('cost_indication')}**")
                    
                    if rec.get('cuisines'):
                        cuisines = rec.get('cuisines', '').split(', ')
                        st.markdown(f"**🍽 {', '.join(cuisines[:3])}{'...' if len(cuisines) > 3 else ''}**")
                    
                    if rec.get('location'):
                        st.markdown(f"**📍 {rec.get('location')}**")
                
                with details_col2:
                    if rec.get('reasons'):
                        st.markdown("**Why we recommend this:**")
                        for reason in rec.get('reasons', [])[:2]:  # Show top 2 reasons
                            st.markdown(f"• {reason}")
                    
                    if rec.get('highlights'):
                        st.markdown("**Highlights:**")
                        highlights_text = ', '.join(rec.get('highlights', [])[:3])  # Show top 3 highlights
                        st.markdown(f"*{highlights_text}*")
                
                # Match score
                if rec.get('match_score'):
                    score = rec.get('match_score', 0) * 100
                    st.progress(score / 100, text=f"Match: {score:.1f}%")
                
                st.markdown("---")
    
    def _get_rating_stars(self, rating: float) -> str:
        """Get star rating display."""
        if rating >= 4.5:
            return "⭐⭐⭐⭐⭐⭐"
        elif rating >= 4.0:
            return "⭐⭐⭐⭐"
        elif rating >= 3.5:
            return "⭐⭐⭐"
        elif rating >= 3.0:
            return "⭐⭐"
        elif rating >= 2.5:
            return "⭐"
        else:
            return "☆"
    
    def display_main_content(self):
        """Display main content area with modern design."""
        # App header
        st.markdown("""
        <div class="app-header">
            <h1 class="app-title">🍽 AI Restaurant Finder</h1>
            <p style="font-size: 1.1rem; opacity: 0.8; margin-top: 0.5rem;">
                Get personalized restaurant recommendations powered by advanced AI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        st.markdown("### 🚀 Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h4 style="color: #667eea; margin-bottom: 0.5rem;">🤖 AI-Powered</h4>
                <p style="font-size: 0.9rem;">Advanced LLM integration</p>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h4 style="color: #667eea; margin-bottom: 0.5rem;">🎯 Personalized</h4>
                <p style="font-size: 0.9rem;">Tailored to your taste</p>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h4 style="color: #667eea; margin-bottom: 0.5rem;">⚡ Instant</h4>
                <p style="font-size: 0.9rem;">Quick response time</p>
            </div>
            """, unsafe_allow_html=True)
        
        # How it works
        st.markdown("### 📋 How It Works")
        
        steps = [
            "📍 Tell us your location and preferences",
            "🤖 Our AI analyzes restaurants matching your criteria", 
            "⭐ Get ranked recommendations with explanations",
            "🍽️ Choose your perfect dining spot"
        ]
        
        for step in steps:
            st.markdown(f"**{step}**")
        
        # Sample recommendations toggle
        if st.checkbox("🎲 Show Sample Recommendations", help="View sample recommendation cards"):
            self.display_sample_recommendations()
    
    def display_sample_recommendations(self):
        """Display sample recommendations with modern card design."""
        st.markdown("### 🎨 Sample Recommendations")
        
        sample_data = [
            {
                "restaurant_name": "Bella Italia",
                "rating": 4.5,
                "cost_indication": "Moderate",
                "location": "Koramangala",
                "cuisines": "Italian, Continental",
                "reasons": ["Perfect Italian cuisine match", "Excellent rating", "Great ambiance"],
                "highlights": ["Authentic pasta", "Wine selection", "Cozy atmosphere"],
                "match_score": 0.92
            },
            {
                "restaurant_name": "Spice Garden",
                "rating": 4.2,
                "cost_indication": "Budget-friendly",
                "location": "Indiranagar",
                "cuisines": "North Indian, Chinese",
                "reasons": ["Great value", "Authentic flavors", "Family-friendly"],
                "highlights": ["Traditional recipes", "Vegetarian options", "Quick service"],
                "match_score": 0.88
            }
        ]
        
        for i, rec in enumerate(sample_data, 1):
            with st.container():
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #667eea; font-size: 1.2rem;">
                            {i}. {rec['restaurant_name']}
                        </h3>
                        {self._get_rating_stars(rec['rating'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Restaurant details
                details_col1, details_col2 = st.columns(2)
                
                with details_col1:
                    st.markdown(f"**💰 {rec['cost_indication']}**")
                    st.markdown(f"**📍 {rec['location']}**")
                    st.markdown(f"**🍽 {', '.join(rec['cuisines'])}**")
                
                with details_col2:
                    st.markdown("**Why we recommend this:**")
                    for reason in rec['reasons'][:2]:
                        st.markdown(f"• {reason}")
                    
                    st.markdown("**Highlights:**")
                    highlights_text = ', '.join(rec['highlights'][:3])
                    st.markdown(f"*{highlights_text}*")
                
                # Match score
                st.progress(rec['match_score'], text=f"Match: {rec['match_score']*100:.1f}%")
                
                st.markdown("---")
    
    def display_footer(self):
        """Display modern footer."""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; margin-top: 2rem; padding: 2rem; background: rgba(255,255,255,0.02); border-radius: 8px;'>
            <p style='margin: 0; font-size: 0.9rem;'>
                🚀 <strong>AI Restaurant Finder</strong>
            </p>
            <p style='margin: 0.5rem 0 0 1rem; font-size: 0.8rem; opacity: 0.7;'>
                Powered by <strong>Advanced AI</strong> • Built with <strong>Streamlit</strong> • <strong>Production Ready</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # API status
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("🟢 API Status: Online")
            else:
                st.error("🔴 API Status: Error")
        except:
            st.warning("🟡 API Status: Offline")
    
    def run(self):
        """Run the modern Streamlit application."""
        # Sidebar for preferences
        with st.sidebar:
            user_preferences = self.get_user_preferences()
            
            # Get recommendations button
            if st.button("🎯 Get Recommendations", type="primary", use_container_width=True):
                self.get_and_display_recommendations(user_preferences)
        
        # Main content area
        self.display_main_content()
        
        # Footer
        self.display_footer()


def create_modern_streamlit_app(api_base_url: str = "http://localhost:8000"):
    """
    Create modern Streamlit app instance.
    
    Args:
        api_base_url: Base URL for the recommendation API
    """
    app = ModernRestaurantApp(api_base_url)
    app.run()


if __name__ == "__main__":
    # Run modern Streamlit app
    create_modern_streamlit_app()
