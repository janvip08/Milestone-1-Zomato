"""
Premium AI Restaurant Recommendation App - Clean Layout Only
Completely refactored to remove all old Streamlit components and render only the new premium UI
"""

import os
import sys
import streamlit as st
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PremiumAIRestaurantApp:
    """Premium AI Streamlit app with clean layout - no legacy components"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize premium AI Streamlit app with clean layout.
        
        Args:
            api_base_url: Base URL for the recommendation API
        """
        self.api_base_url = api_base_url
        self.setup_page_config()
        self.setup_premium_css()
    
    def setup_page_config(self):
        """Setup premium page configuration with centered layout."""
        st.set_page_config(
            page_title="✨ AI Restaurant Finder",
            page_icon="🤖",
            layout="centered",
            initial_sidebar_state="collapsed",
            menu_items={
                'Get Help': None,
                'Report a bug': "https://github.com/janvip08/Milestone-1-Zomato/issues",
                'About': "AI-Powered Restaurant Recommendation System"
            }
        )
    
    def setup_premium_css(self):
        """Setup premium CSS with complete override of Streamlit defaults."""
        st.markdown("""
        <style>
        /* COMPLETE STREAMLIT OVERRIDE - HIDE ALL DEFAULT ELEMENTS */
        
        /* Hide sidebar completely */
        .css-1lcbmhc,
        .css-1outcr7,
        .stSidebar,
        [data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
            min-width: 0px !important;
            max-width: 0px !important;
        }
        
        /* Hide main menu and header */
        .stMainMenu,
        .stHeader,
        .stToolbar,
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Hide deploy button and other default elements */
        .stDeployButton,
        [data-testid="stDeployButton"] {
            display: none !important;
        }
        
        /* Override entire app background */
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
            background-attachment: fixed;
            color: #ffffff;
            overflow-x: hidden;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Override main container to be centered and clean */
        .main .block-container {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 3rem 3.5rem;
            margin: 2rem auto !important;
            max-width: 900px !important;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        /* Remove all default Streamlit spacing */
        .element-container,
        .stVerticalBlock,
        .stBlock {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Glassmorphism search container */
        .search-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 
                0 4px 20px rgba(0, 0, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
        
        /* AI Header styling */
        .ai-header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
        }
        
        .ai-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
            animation: glow 3s ease-in-out infinite alternate;
        }
        
        .ai-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 400;
            margin-top: 0.5rem;
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.5)); }
            to { filter: drop-shadow(0 0 30px rgba(118, 75, 162, 0.8)); }
        }
        
        /* Override all Streamlit input styles */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            color: #ffffff !important;
            font-size: 15px !important;
            transition: all 0.3s ease !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            background: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(102, 126, 234, 0.5) !important;
            box-shadow: 
                0 0 0 3px rgba(102, 126, 234, 0.1),
                inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            outline: none !important;
        }
        
        /* Override slider styling */
        .stSlider > div > div > div {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            color: #ffffff !important;
        }
        
        /* Override radio button styling */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }
        
        .stRadio > div > label {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        
        /* Override button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 18px 40px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                0 8px 24px rgba(102, 126, 234, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
            width: 100% !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 
                0 12px 32px rgba(102, 126, 234, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* Override all default Streamlit widgets */
        .stSelectbox,
        .stTextInput,
        .stTextArea,
        .stSlider,
        .stRadio,
        .stButton {
            margin-bottom: 1rem !important;
        }
        
        /* Recommendation cards with glassmorphism */
        .recommendation-card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 
                0 4px 20px rgba(0, 0, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
        
        .recommendation-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .recommendation-card:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                0 12px 40px rgba(0, 0, 0, 0.3),
                0 0 40px rgba(102, 126, 234, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
        }
        
        .recommendation-card:hover::before {
            opacity: 1;
        }
        
        /* Restaurant name styling */
        .restaurant-name {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Cuisine tags */
        .cuisine-tag {
            display: inline-block;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #ffffff;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Rating badge */
        .rating-badge {
            display: inline-flex;
            align-items: center;
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            color: #333;
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
        }
        
        /* Match score styling */
        .match-score {
            background: linear-gradient(135deg, #00c896, #00ff88);
            color: #000;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: 700;
            font-size: 1rem;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0, 200, 150, 0.3);
        }
        
        /* AI explanation section */
        .ai-explanation {
            background: rgba(102, 126, 234, 0.1);
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-top: 1rem;
            backdrop-filter: blur(10px);
        }
        
        .ai-explanation-title {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
        }
        
        .ai-explanation-text {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        /* Loading animation */
        .loading-animation {
            text-align: center;
            padding: 3rem;
        }
        
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Empty state styling */
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        /* Override all Streamlit default margins and padding */
        .streamlit-container,
        .main,
        .stApp {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 2rem 1.5rem !important;
                margin: 1rem auto !important;
            }
            
            .ai-title {
                font-size: 2.5rem;
            }
            
            .ai-subtitle {
                font-size: 1rem;
            }
            
            .search-container {
                padding: 1.5rem;
            }
            
            .recommendation-card {
                padding: 1.5rem;
            }
            
            .restaurant-name {
                font-size: 1.5rem;
            }
            
            .stButton > button {
                padding: 16px 32px !important;
                font-size: 14px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_ai_header(self):
        """Render AI branding header."""
        st.markdown("""
        <div class="ai-header">
            <h1 class="ai-title">✨ AI Restaurant Finder</h1>
            <p class="ai-subtitle">Discover perfect dining experiences powered by artificial intelligence</p>
        </div>
        """, unsafe_allow_html=True)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from glassmorphism search container - NO SIDEBAR."""
        preferences = {}
        
        # Search container - NO SIDEBAR USAGE
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Two column layout for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            # Location input
            preferences["location"] = st.text_input(
                "📍 City/Area",
                placeholder="e.g., Koramangala, Indiranagar",
                help="Enter your preferred location"
            )
        
        with col2:
            # Cuisine dropdown
            cuisine_options = ["", "Italian", "Indian", "Chinese", "Japanese", "Mexican", "Thai", "Continental", "American", "Korean", "French"]
            preferences["cuisine"] = st.selectbox(
                "🍽 Cuisine Type",
                options=cuisine_options,
                index=0,
                help="Select your preferred cuisine"
            )
        
        # Budget selection - horizontal radio buttons
        preferences["budget"] = st.radio(
            "💰 Budget Range",
            options=["Budget Friendly", "Moderate", "Premium", "Fine Dining"],
            horizontal=True,
            help="Choose your preferred budget range"
        )
        
        # Rating slider
        preferences["min_rating"] = st.slider(
            "⭐ Minimum Rating",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.5,
            help="Minimum restaurant rating"
        )
        
        # Additional preferences
        preferences["additional_constraints"] = st.text_area(
            "📝 Additional Preferences",
            placeholder="e.g., Outdoor seating, Live music, Family-friendly, Vegan options...",
            help="Any specific requirements or preferences"
        )
        
        # Number of recommendations
        preferences["top_n"] = st.selectbox(
            "🎯 Number of Recommendations",
            options=[3, 5, 8, 10],
            index=1,
            help="How many recommendations would you like?"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return preferences
    
    def render_cta_button(self):
        """Render gradient CTA button - centered."""
        if st.button("🚀 Find My Perfect Restaurant", key="cta_button", help="Get AI-powered restaurant recommendations"):
            return True
        return False
    
    def get_recommendations(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations from the API."""
        try:
            payload = {
                "preferences": {
                    "location": preferences.get("location", ""),
                    "cuisine": preferences.get("cuisine", ""),
                    "budget": preferences.get("budget", ""),
                    "min_rating": preferences.get("min_rating", 4.0),
                    "additional_constraints": preferences.get("additional_constraints", ""),
                    "top_n": preferences.get("top_n", 5)
                },
                "max_recommendations": preferences.get("top_n", 5),
                "response_type": "recommendation",
                "include_explanations": True
            }
            
            response = requests.post(
                f"{self.api_base_url}/recommend",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def render_recommendation_card(self, recommendation: Dict[str, Any], index: int):
        """Render individual recommendation card with glassmorphism."""
        st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
        
        # Restaurant name and rank
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<h3 class="restaurant-name">{recommendation.get("restaurant_name", "Unknown Restaurant")}</h3>', unsafe_allow_html=True)
        with col2:
            if "rank" in recommendation:
                st.markdown(f'<div class="match-score">#{recommendation["rank"]}</div>', unsafe_allow_html=True)
        
        # Cuisine and rating
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if "cuisine" in recommendation:
                st.markdown(f'<span class="cuisine-tag">{recommendation["cuisine"]}</span>', unsafe_allow_html=True)
        with col2:
            if "rating" in recommendation:
                st.markdown(f'<div class="rating-badge">⭐ {recommendation["rating"]}</div>', unsafe_allow_html=True)
        with col3:
            if "match_score" in recommendation:
                score = recommendation["match_score"]
                st.markdown(f'<div class="match-score">{score}% Match</div>', unsafe_allow_html=True)
        
        # Location and price
        col1, col2 = st.columns(2)
        with col1:
            if "location" in recommendation:
                st.markdown(f"📍 {recommendation['location']}")
        with col2:
            if "price_indication" in recommendation:
                st.markdown(f"💰 {recommendation['price_indication']}")
        
        # AI explanation
        if "reasons" in recommendation and recommendation["reasons"]:
            reasons_text = " • ".join(recommendation["reasons"])
            st.markdown(f"""
            <div class="ai-explanation">
                <div class="ai-explanation-title">🤖 Why this restaurant?</div>
                <div class="ai-explanation-text">{reasons_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
    
    def render_loading_state(self):
        """Render loading animation."""
        st.markdown("""
        <div class="loading-animation">
            <div class="loading-spinner"></div>
            <h3>🤖 AI is analyzing your preferences...</h3>
            <p>Finding the perfect restaurants for you</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_empty_state(self):
        """Render empty state."""
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🍽️</div>
            <h3>No restaurants found</h3>
            <p>Try adjusting your preferences or explore different locations</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the main application - CLEAN LAYOUT ONLY."""
        # Render AI header
        self.render_ai_header()
        
        # Get user preferences - NO SIDEBAR
        preferences = self.get_user_preferences()
        
        # CTA button
        if self.render_cta_button():
            # Show loading state
            self.render_loading_state()
            
            # Get recommendations
            recommendations = self.get_recommendations(preferences)
            
            if recommendations:
                st.markdown("---")
                st.markdown('<h2 style="text-align: center; margin-bottom: 2rem;">🎯 Your AI Recommendations</h2>', unsafe_allow_html=True)
                
                # Render recommendations - ONLY NEW STYLE
                if "recommendations" in recommendations and recommendations["recommendations"]:
                    for i, rec in enumerate(recommendations["recommendations"]):
                        self.render_recommendation_card(rec, i + 1)
                else:
                    self.render_empty_state()
                
                # Summary if available
                if "summary" in recommendations:
                    st.markdown("---")
                    st.markdown(f"**📊 Summary:** {recommendations['summary']}")
            else:
                st.error("❌ Failed to get recommendations. Please try again.")

# Main execution
if __name__ == "__main__":
    app = PremiumAIRestaurantApp()
    app.run()
