"""Recommendation API Server: FastAPI-based REST API for restaurant recommendations."""

from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug environment variable loading
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    masked_key = groq_api_key[:4] + "****" + groq_api_key[-4:] if len(groq_api_key) > 8 else groq_api_key
    print(f"GROQ_API_KEY loaded successfully: {masked_key}")
else:
    print("GROQ_API_KEY not found in environment variables")
    print("Please set GROQ_API_KEY in your .env file or system environment")

from phase2 import PreferenceParser, FilterEngine, RankerV1
from phase3 import Phase3Pipeline, create_default_config
from .groq_provider import create_phase3_config_with_groq
from .error_handler import ErrorHandler, FallbackHandler


# Pydantic models for API
class UserPreferences(BaseModel):
    """User preferences model."""
    location: str = Field(..., description="Preferred location")
    cuisine: Optional[str] = Field(None, description="Preferred cuisine type")
    min_rating: Optional[float] = Field(3.0, ge=0, le=5, description="Minimum rating")
    max_cost_for_two: Optional[int] = Field(None, ge=0, description="Maximum cost for two")
    preferred_cuisines: Optional[List[str]] = Field(None, description="List of preferred cuisines")
    budget_category: Optional[str] = Field(None, description="Budget category")
    meal_type: Optional[str] = Field(None, description="Meal type")
    occasion: Optional[str] = Field(None, description="Occasion")
    additional_requirements: Optional[str] = Field(None, description="Additional requirements")


class RecommendationRequest(BaseModel):
    """Recommendation request model."""
    preferences: UserPreferences
    max_recommendations: Optional[int] = Field(5, ge=1, le=20, description="Maximum recommendations to return")
    response_type: Optional[str] = Field("recommendation", description="Type of response: recommendation, ranking, explanation")
    include_explanations: Optional[bool] = Field(True, description="Include AI explanations")


class RecommendationResponse(BaseModel):
    """Recommendation response model."""
    recommendations: List[Dict[str, Any]]
    summary: str
    total_matches: int
    response_time_ms: int
    metadata: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class RecommendationAPI:
    """FastAPI-based recommendation server."""
    
    def __init__(self, groq_api_key: str, data_path: str = "data/processed/restaurants.csv"):
        """
        Initialize the API server.
        
        Args:
            groq_api_key: Groq API key for LLM
            data_path: Path to processed restaurant data
        """
        self.logger = logging.getLogger(__name__)
        self.groq_api_key = groq_api_key
        self.data_path = data_path
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Restaurant Recommendation API",
            description="AI-powered restaurant recommendations using Groq LLM",
            version="1.0.0"
        )
        
        # Add CORS middleware (Configurable for production Vercel frontend)
        allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
        allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.error_handler = ErrorHandler()
        self.fallback_handler = FallbackHandler()
        
        # Initialize Phase 2 components
        self.preference_parser = PreferenceParser()
        self.filter_engine = FilterEngine()
        self.ranker_v1 = RankerV1()
        
        # Initialize Phase 3 pipeline with Groq
        print(f"Initializing Phase 3 pipeline with Groq...")
        self.phase3_config = create_phase3_config_with_groq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            max_tokens=1500,
            temperature=0.7
        )
        print(f"Phase 3 config created successfully")
        print(f"LLM provider: {self.phase3_config.llm_config.provider}")
        print(f"Model: {self.phase3_config.llm_config.model_name}")
        print(f"Max candidates: {self.phase3_config.max_candidates}")
        
        self.phase3_pipeline = Phase3Pipeline(self.phase3_config)
        print(f"Phase 3 pipeline initialized successfully")
        
        # Load data
        self.restaurants_data = self._load_restaurant_data()
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("Recommendation API initialized")
    
    def _load_restaurant_data(self) -> List[Dict[str, Any]]:
        """Load restaurant data from file."""
        try:
            import pandas as pd
            self.logger.info(f"Loading restaurant data from: {self.data_path}")
            
            # Try to load CSV first
            if self.data_path.endswith('.csv'):
                df = pd.read_csv(self.data_path)
                self.logger.info(f"Successfully loaded CSV with {len(df)} restaurants")
                return df.to_dict('records')
            # Fallback to JSON if CSV doesn't exist
            else:
                # Try to load from phase1 processed data
                json_path = "phase1/output/processed_dataset.json"
                try:
                    import json
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    
                    # Convert JSON data to proper format
                    restaurants = []
                    for item in data:
                        if isinstance(item, dict) and 'name' in item:
                            restaurant = {
                                'name': item.get('name', ''),
                                'location': item.get('location', ''),
                                'cuisines': item.get('cuisines', ''),
                                'cost_for_two': item.get('cost_for_two', 0),
                                'rating': item.get('rating', 0.0),
                                'cost_indication': self._get_cost_indication(item.get('cost_for_two', 0)),
                                'best_for': 'Family Meal',
                                'highlights': ['Good food', 'Reasonable prices'],
                                'reasons': ['Matches your preferences']
                            }
                            restaurants.append(restaurant)
                    
                    self.logger.info(f"Successfully loaded JSON with {len(restaurants)} restaurants")
                    return restaurants
                    
                except FileNotFoundError:
                    self.logger.error(f"JSON data file not found: {json_path}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Failed to load restaurant data: {e}")
            return []
    
    def _get_cost_indication(self, cost_for_two: int) -> str:
        """Get cost indication based on cost for two."""
        if cost_for_two <= 500:
            return "Budget-friendly"
        elif cost_for_two <= 1000:
            return "Moderate"
        elif cost_for_two <= 1500:
            return "Premium"
        else:
            return "Fine Dining"
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "message": "Restaurant Recommendation API",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                # Test Groq connection
                groq_status = self.phase3_pipeline.llm_client.test_connection()
                
                return {
                    "status": "healthy",
                    "groq_connection": groq_status,
                    "restaurants_loaded": len(self.restaurants_data),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Health check failed: {e}")
        
        @self.app.post("/recommend", response_model=RecommendationResponse)
        async def get_recommendations(request: RecommendationRequest):
            """Get restaurant recommendations."""
            start_time = datetime.now()
            
            try:
                self.logger.info(f"Received recommendation request: {request.preferences.dict()}")
                
                # Parse preferences
                parsed_preferences = self.preference_parser.parse(
                    request.preferences.dict()
                )
                self.logger.info(f"Parsed preferences: {parsed_preferences}")
                
                # Filter candidates
                candidates = self.filter_engine.filter(
                    self.restaurants_data, parsed_preferences
                )
                self.logger.info(f"Found {len(candidates)} candidates after filtering")
                
                if not candidates:
                    self.logger.warning("No candidates found after filtering")
                    # Use fallback handler
                    fallback_response = self.fallback_handler.handle_no_matches(
                        parsed_preferences
                    )
                    return RecommendationResponse(
                        recommendations=fallback_response.get("recommendations", []),
                        summary=fallback_response.get("summary", "No restaurants found matching your criteria. Here are some popular alternatives."),
                        total_matches=fallback_response.get("total_matches", 0),
                        response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                        metadata={"fallback_used": True, "suggestions": fallback_response.get("suggestions", [])}
                    )
                
                # Get recommendations using Phase 3
                if request.response_type == "recommendation":
                    self.logger.info("Generating recommendations using Phase 3 pipeline")
                    result = self.phase3_pipeline.generate_recommendations(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                    self.logger.info(f"Phase 3 result: {result}")
                elif request.response_type == "ranking":
                    self.logger.info("Generating ranking using Phase 3 pipeline")
                    result = self.phase3_pipeline.generate_ranking(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                    self.logger.info(f"Phase 3 ranking result: {result}")
                elif request.response_type == "explanation":
                    self.logger.info("Generating explanations using Phase 3 pipeline")
                    result = self.phase3_pipeline.generate_explanations(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                    self.logger.info(f"Phase 3 explanation result: {result}")
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown response type: {request.response_type}")
                
                # Calculate response time
                response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                final_recommendations = result.get("recommendations", result.get("ranked_restaurants", result.get("detailed_explanations", [])))
                
                self.logger.info(f"Final recommendations to return: {final_recommendations}")
                
                return RecommendationResponse(
                    recommendations=final_recommendations,
                    summary=result.get("summary", f"Found {len(final_recommendations)} recommendations for {parsed_preferences.get('location', 'your location')}"),
                    total_matches=len(candidates),
                    response_time_ms=response_time,
                    metadata=result.get("metadata", {"pipeline_used": "phase3", "candidates_count": len(candidates)})
                )
                
            except Exception as e:
                self.logger.error(f"Recommendation generation failed: {e}")
                error_response = self.error_handler.handle_error(e, request.preferences.dict())
                raise HTTPException(
                    status_code=error_response["status_code"],
                    detail=error_response["message"]
                )
        
        @self.app.get("/restaurants")
        async def get_restaurants(
            location: Optional[str] = None,
            cuisine: Optional[str] = None,
            limit: int = 50
        ):
            """Get restaurant list with optional filtering."""
            try:
                restaurants = self.restaurants_data
                
                if location:
                    restaurants = [r for r in restaurants if location.lower() in r.get("location", "").lower()]
                
                if cuisine:
                    restaurants = [r for r in restaurants if cuisine.lower() in r.get("cuisines", "").lower()]
                
                return {
                    "restaurants": restaurants[:limit],
                    "total_found": len(restaurants),
                    "filters_applied": {"location": location, "cuisine": cuisine}
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get restaurants: {e}")
        
        @self.app.get("/models")
        async def get_available_models():
            """Get available LLM models."""
            try:
                from .groq_provider import GroqProvider
                groq_provider = GroqProvider(self.phase3_config)
                return {
                    "available_models": groq_provider.list_available_models(),
                    "current_model": self.phase3_config.model_name
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get models: {e}")
        
        @self.app.post("/feedback")
        async def submit_feedback(
            recommendation_id: str,
            rating: int,
            comment: Optional[str] = None
        ):
            """Submit feedback for recommendations."""
            # Placeholder for feedback collection
            return {
                "message": "Feedback submitted successfully",
                "recommendation_id": recommendation_id,
                "rating": rating,
                "comment": comment
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the API server."""
        self.logger.info(f"Starting API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info" if debug else "warning")


def create_app(groq_api_key: str, data_path: str = "data/processed/restaurants.csv") -> FastAPI:
    """
    Create FastAPI app instance.
    
    Args:
        groq_api_key: Groq API key
        data_path: Path to restaurant data
        
    Returns:
        FastAPI app instance
    """
    api = RecommendationAPI(groq_api_key, data_path)
    return api.app


if __name__ == "__main__":
    import os
    
    # Get API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        exit(1)
    
    # Create and run API
    api = RecommendationAPI(groq_api_key)
    api.run(debug=True)
