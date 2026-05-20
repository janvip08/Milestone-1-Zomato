"""
AI Restaurant Recommendation App - Premium Glassmorphism Design
Modern UI matching reference screenshots with glassmorphism effects and AI branding
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

class AIRestaurantApp:
    """Premium AI Streamlit app with glassmorphism design"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize AI Streamlit app with modern design.
        
        Args:
            api_base_url: Base URL for the recommendation API
        """
        self.api_base_url = api_base_url
        self.setup_page_config()
        self.setup_glassmorphism_css()
    
    def setup_page_config(self):
        """Setup premium page configuration."""
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
    
    def setup_glassmorphism_css(self):
        """Setup glassmorphism CSS design matching reference screenshots."""
        st.markdown("""
        <style>
        /* Global styles and glassmorphism background */
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
            background-attachment: fixed;
            color: #ffffff;
            overflow-x: hidden;
        }
        
        /* Glassmorphism main container */
        .main .block-container {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 3rem 3.5rem;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Hide sidebar completely */
        .css-1lcbmhc {
            display: none;
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
        
        /* Input styling with glassmorphism */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            color: #ffffff;
            font-size: 15px;
            transition: all 0.3s ease;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stTextInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(102, 126, 234, 0.5);
            box-shadow: 
                0 0 0 3px rgba(102, 126, 234, 0.1),
                inset 0 2px 4px rgba(0, 0, 0, 0.1);
            outline: none;
        }
        
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            color: #ffffff;
            font-size: 15px;
            transition: all 0.3s ease;
        }
        
        .stSelectbox > div > div > select:focus {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(102, 126, 234, 0.5);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        /* Slider styling */
        .stSlider > div > div > div {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            color: #ffffff;
        }
        
        /* Budget selection cards */
        .budget-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .budget-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .budget-card:hover {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(102, 126, 234, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        .budget-card.selected {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
            border: 1px solid rgba(102, 126, 234, 0.7);
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }
        
        /* CTA Button styling */
        .cta-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 18px 40px;
            font-weight: 700;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 
                0 8px 24px rgba(102, 126, 234, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 
                0 12px 32px rgba(102, 126, 234, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
        
        .cta-button:active {
            transform: translateY(-1px);
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
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 2rem 1.5rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
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
            
            .cta-button {
                padding: 16px 32px;
                font-size: 14px;
            }
        }
        
        /* Hide streamlit default elements */
        .stDeployButton, .stHeader {
            display: none;
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
        """Get user preferences from glassmorphism search container."""
        preferences = {}
        
        # Search container
        with st.container():
            st.markdown('<div class="search-container">', unsafe_allow_html=True)
            
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
            
            # Budget selection cards
            st.markdown("### 💰 Budget Range")
            budget_options = ["Budget Friendly", "Moderate", "Premium", "Fine Dining"]
            selected_budget = st.radio(
                "Select your budget preference:",
                options=budget_options,
                horizontal=True,
                help="Choose your preferred budget range"
            )
            preferences["budget"] = selected_budget
            
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
        """Render gradient CTA button."""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
        with st.container():
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
        """Run the main application."""
        # Render AI header
        self.render_ai_header()
        
        # Get user preferences
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
                
                # Render recommendations
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
    app = AIRestaurantApp()
    app.run()
