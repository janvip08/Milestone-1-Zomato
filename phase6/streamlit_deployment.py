"""
Phase 6: Streamlit Production Deployment
Production-ready Streamlit app configuration for cloud deployment
"""

import os
import sys
import streamlit as st
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitDeploymentManager:
    """Manages Streamlit app deployment and configuration"""
    
    def __init__(self):
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.app_name = os.getenv('APP_NAME', 'Restaurant Recommender')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.version = os.getenv('APP_VERSION', '1.0.0')
        
    def get_api_health(self) -> Dict[str, Any]:
        """Check backend API health status"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        api_health = self.get_api_health()
        
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "api_status": api_health,
            "streamlit_status": "healthy",
            "deployment_type": "streamlit_cloud"
        }
    
    def configure_production_settings(self):
        """Configure production settings for Streamlit"""
        st.set_page_config(
            page_title=self.app_name,
            page_icon="🍽",
            layout="centered",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': "https://github.com/janvip08/Milestone-1-Zomato/issues",
                'About': None
            }
        )
        
        # Production theme
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .stButton > button {
            background-color: #FF6B6B;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton > button:hover {
            background-color: #FF5252;
        }
        </style>
        """, unsafe_allow_html=True)

def create_production_ui():
    """Create production Streamlit UI"""
    manager = StreamlitDeploymentManager()
    manager.configure_production_settings()
    
    # Header
    st.title("🍽 Restaurant Recommendation System")
    st.markdown("---")
    
    # System Status Sidebar
    with st.sidebar:
        st.header("📊 System Status")
        
        system_status = manager.get_system_status()
        
        # Display status indicators
        col1, col2 = st.columns(2)
        
        with col1:
            if system_status["api_status"]["status"] == "healthy":
                st.success("🟢 API Healthy")
            else:
                st.error("🔴 API Error")
                
        with col2:
            st.success("🟢 Streamlit Healthy")
        
        st.markdown("---")
        
        # System Information
        st.subheader("📋 System Information")
        st.json(system_status, expanded=False)
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        if st.button("🔄 Refresh Status", key="refresh_status"):
            st.rerun()
            
        if st.button("🧪 Test API", key="test_api"):
            with st.spinner("Testing API..."):
                test_result = manager.get_api_health()
                st.json(test_result)
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Production Features")
        
        # Feature Cards
        feature_col1, feature_col2 = st.columns(2)
        
        with feature_col1:
            st.markdown("""
            ### 🤖 AI-Powered Recommendations
            - Advanced LLM integration with Groq
            - Personalized restaurant suggestions
            - Real-time recommendation generation
            - Multi-cuisine support
            """)
            
        with feature_col2:
            st.markdown("""
            ### 🌐 Production Deployment
            - Streamlit Cloud hosting
            - FastAPI backend integration
            - Real-time health monitoring
            - Production-grade security
            """)
        
        st.markdown("---")
        
        # API Integration Status
        st.subheader("🔗 API Integration")
        
        api_health = manager.get_api_health()
        if api_health["status"] == "healthy":
            st.success("✅ Backend API is connected and healthy")
        else:
            st.error("❌ Backend API connection failed")
            st.error(f"Error: {api_health.get('error', 'Unknown error')}")
        
        # API Usage Example
        st.markdown("#### 📝 API Usage Example")
        st.code("""
        import requests
        
        # Get recommendations
        response = requests.post('https://your-api-url.com/recommend', json={
            'location': 'Bangalore',
            'budget': 2000,
            'cuisine': 'Italian',
            'rating': 4.0
        })
        
        recommendations = response.json()
        """, language="python")
    
    with col2:
        st.header("📈 Analytics")
        
        # Mock Analytics (in production, this would connect to real analytics)
        st.markdown("### 📊 Today's Stats")
        st.metric("Total Requests", "1,234", delta="123")
        st.metric("Success Rate", "98.5%", delta="0.3%")
        st.metric("Avg Response Time", "750ms", delta="-50ms")
        
        st.markdown("---")
        
        st.markdown("### 🌍 Deployment Info")
        st.markdown(f"""
        - **Environment**: {manager.environment}
        - **Version**: {manager.version}
        - **API URL**: {manager.api_base_url}
        - **Deployed**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>🚀 Production Restaurant Recommendation System</p>
        <p>Built with ❤️ using Streamlit + FastAPI + Groq LLM</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main entry point for production Streamlit app"""
    try:
        create_production_ui()
        
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error(f"Application Error: {str(e)}")
        st.error("Please check the logs or contact support")

if __name__ == "__main__":
    main()
