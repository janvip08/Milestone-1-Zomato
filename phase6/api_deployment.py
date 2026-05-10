"""
Phase 6: FastAPI Production Deployment
Production-ready FastAPI deployment scripts for cloud platforms
"""

import os
import sys
import subprocess
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIDeploymentManager:
    """Manages FastAPI backend deployment and configuration"""
    
    def __init__(self):
        self.api_host = os.getenv('API_HOST', '0.0.0.0')
        self.api_port = int(os.getenv('API_PORT', '8000'))
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/restaurants.db')
        
    def create_production_config(self) -> Dict[str, Any]:
        """Create production configuration"""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "workers": 4,
            "log_level": "INFO",
            "environment": self.environment,
            "cors_origins": [
                "https://your-streamlit-app.streamlit.app",
                "https://localhost:8501"
            ],
            "rate_limit": {
                "requests_per_minute": 60,
                "burst_size": 10
            },
            "security": {
                "ssl_required": True,
                "api_key_required": True
            }
        }
    
    def create_dockerfile(self) -> str:
        """Create production Dockerfile"""
        return '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
'''
    
    def create_docker_compose(self) -> str:
        """Create production docker-compose.yml"""
        return '''
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///data/restaurants.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
'''
    
    def create_railway_config(self) -> Dict[str, Any]:
        """Create Railway deployment configuration"""
        return {
            "build": {
                "builder": "NIXPACKS",
                "buildCommand": "pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port $PORT",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
            },
            "environment": {
                "GROQ_API_KEY": "@groq_api_key",
                "API_HOST": "0.0.0.0",
                "API_PORT": "$PORT",
                "ENVIRONMENT": "production",
                "DATABASE_URL": "sqlite:///data/restaurants.db"
            },
            "ports": {
                "8000": "HTTP"
            }
        }
    
    def create_render_config(self) -> Dict[str, Any]:
        """Create Render deployment configuration"""
        return {
            "type": "PSERVICE",
            "name": "restaurant-api",
            "env": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envVars": [
                {"key": "GROQ_API_KEY", "value": "@groq_api_key"},
                {"key": "API_HOST", "value": "0.0.0.0"},
                {"key": "API_PORT", "value": "$PORT"},
                {"key": "ENVIRONMENT", "value": "production"}
            ],
            "healthCheckPath": "/health",
            "disk": {
                "name": "restaurant-api-disk",
                "mountPath": "/app/data",
                "sizeGB": 10
            }
        }
    
    def deploy_to_railway(self) -> bool:
        """Deploy to Railway platform"""
        try:
            logger.info("Starting Railway deployment...")
            
            # Check if Railway CLI is installed
            result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Railway CLI not found. Installing...")
                subprocess.run(['npm', 'install', '-g', '@railway/cli'])
            
            # Create railway.json configuration
            config = self.create_railway_config()
            with open('railway.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            # Deploy
            result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Railway deployment successful")
                return True
            else:
                logger.error(f"Railway deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Railway deployment error: {str(e)}")
            return False
    
    def deploy_to_render(self) -> bool:
        """Deploy to Render platform"""
        try:
            logger.info("Starting Render deployment...")
            
            # Create render.yaml configuration
            config = self.create_render_config()
            with open('render.yaml', 'w') as f:
                json.dump(config, f, indent=2)
            
            # Instructions for manual deployment
            logger.info("Render configuration created. Please deploy manually via Render dashboard.")
            return True
            
        except Exception as e:
            logger.error(f"Render deployment error: {str(e)}")
            return False
    
    def test_deployment(self, api_url: str) -> Dict[str, Any]:
        """Test deployed API"""
        try:
            # Test health endpoint
            health_response = requests.get(f"{api_url}/health", timeout=10)
            
            # Test recommendation endpoint
            test_payload = {
                "location": "Bangalore",
                "budget": 2000,
                "cuisine": "Italian",
                "rating": 4.0
            }
            
            recommend_response = requests.post(
                f"{api_url}/recommend",
                json=test_payload,
                timeout=30
            )
            
            return {
                "health_check": {
                    "status_code": health_response.status_code,
                    "response_time": health_response.elapsed.total_seconds(),
                    "success": health_response.status_code == 200
                },
                "recommendation_test": {
                    "status_code": recommend_response.status_code,
                    "response_time": recommend_response.elapsed.total_seconds(),
                    "success": recommend_response.status_code == 200,
                    "has_recommendations": len(recommend_response.json().get("recommendations", [])) > 0
                },
                "overall_status": "healthy" if health_response.status_code == 200 else "unhealthy"
            }
            
        except Exception as e:
            logger.error(f"Deployment test failed: {str(e)}")
            return {
                "error": str(e),
                "overall_status": "error"
            }
    
    def create_deployment_script(self) -> str:
        """Create deployment script for production"""
        return '''#!/bin/bash

# Production Deployment Script
echo "🚀 Deploying Restaurant Recommender API..."

# Check environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Production Environment Detected"
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run database migrations
    python -c "
import sqlite3
conn = sqlite3('data/restaurants.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    rating REAL NOT NULL,
    cost_for_two INTEGER NOT NULL,
    location TEXT NOT NULL,
    specialties TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
conn.close()
print('Database initialized')
"
    
    # Start API server
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    
else
    echo "🧪 Development Environment"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
'''

def main():
    """Main entry point for API deployment"""
    manager = APIDeploymentManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "deploy-railway":
            success = manager.deploy_to_railway()
            if success:
                print("✅ Railway deployment successful")
            else:
                print("❌ Railway deployment failed")
                
        elif command == "deploy-render":
            success = manager.deploy_to_render()
            if success:
                print("✅ Render deployment configuration created")
            else:
                print("❌ Render deployment failed")
                
        elif command == "test":
            api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
            test_result = manager.test_deployment(api_url)
            print(json.dumps(test_result, indent=2))
            
        elif command == "create-configs":
            # Create all configuration files
            with open('Dockerfile', 'w') as f:
                f.write(manager.create_dockerfile())
            
            with open('docker-compose.yml', 'w') as f:
                f.write(manager.create_docker_compose())
            
            with open('railway.json', 'w') as f:
                json.dump(manager.create_railway_config(), f, indent=2)
            
            with open('render.yaml', 'w') as f:
                json.dump(manager.create_render_config(), f, indent=2)
            
            with open('deploy.sh', 'w') as f:
                f.write(manager.create_deployment_script())
            
            print("✅ All configuration files created")
            
        else:
            print("❌ Unknown command")
            print("Available commands: deploy-railway, deploy-render, test, create-configs")
    else:
        print("📋 API Deployment Manager")
        print("Commands: deploy-railway, deploy-render, test, create-configs")
        print("Example: python api_deployment.py deploy-railway")

if __name__ == "__main__":
    main()
