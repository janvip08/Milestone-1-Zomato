"""Recommendation API Server: FastAPI-based REST API for restaurant recommendations."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..phase2 import PreferenceParser, FilterEngine, RankerV1
from ..phase3 import Phase3Pipeline, create_default_config
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
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
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
        self.phase3_config = create_phase3_config_with_groq(
            groq_api_key=groq_api_key,
            model_name="llama3-8b-8192",
            max_tokens=1500,
            temperature=0.7
        )
        self.phase3_pipeline = Phase3Pipeline(self.phase3_config)
        
        # Load data
        self.restaurants_data = self._load_restaurant_data()
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("Recommendation API initialized")
    
    def _load_restaurant_data(self) -> List[Dict[str, Any]]:
        """Load restaurant data from file."""
        try:
            import pandas as pd
            df = pd.read_csv(self.data_path)
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Failed to load restaurant data: {e}")
            return []
    
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
                # Parse preferences
                parsed_preferences = self.preference_parser.parse_preferences(
                    request.preferences.dict()
                )
                
                # Filter candidates
                candidates = self.filter_engine.filter_restaurants(
                    self.restaurants_data, parsed_preferences
                )
                
                if not candidates:
                    # Use fallback handler
                    fallback_response = self.fallback_handler.handle_no_matches(
                        parsed_preferences
                    )
                    return RecommendationResponse(
                        recommendations=[],
                        summary=fallback_response["message"],
                        total_matches=0,
                        response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                        metadata={"fallback_used": True}
                    )
                
                # Get recommendations using Phase 3
                if request.response_type == "recommendation":
                    result = self.phase3_pipeline.generate_recommendations(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                elif request.response_type == "ranking":
                    result = self.phase3_pipeline.generate_ranking(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                elif request.response_type == "explanation":
                    result = self.phase3_pipeline.generate_explanations(
                        candidates[:request.max_recommendations],
                        parsed_preferences,
                        additional_instructions=request.preferences.additional_requirements
                    )
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown response type: {request.response_type}")
                
                # Calculate response time
                response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return RecommendationResponse(
                    recommendations=result.get("recommendations", result.get("ranked_restaurants", result.get("detailed_explanations", []))),
                    summary=result.get("summary", ""),
                    total_matches=len(candidates),
                    response_time_ms=response_time,
                    metadata=result.get("metadata", {})
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
                    restaurants = [r for r in restaurants if cuisine.lower() in r.get("cuisine", "").lower()]
                
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
