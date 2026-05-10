"""Phase 4 Application Orchestrator: End-to-end application coordination."""

from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass

from phase2 import PreferenceParser, FilterEngine, RankerV1
from phase3 import Phase3Pipeline, create_default_config
from .groq_provider import create_phase3_config_with_groq
from .api_server import RecommendationAPI
from .presentation_layer import PresentationLayer
from .cli_interface import CLIInterface
from .error_handler import ErrorHandler, FallbackHandler, GracefulDegradation


@dataclass
class Phase4Config:
    """Configuration for Phase 4 application."""
    groq_api_key: str
    data_path: str = "data/processed/restaurants.csv"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_host: str = "localhost"
    streamlit_port: int = 8501
    enable_cors: bool = True
    log_level: str = "INFO"
    max_recommendations: int = 10
    response_timeout: int = 30


class Phase4App:
    """Main application orchestrator for Phase 4."""
    
    def __init__(self, config: Phase4Config):
        """
        Initialize the Phase 4 application.
        
        Args:
            config: Phase 4 configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize error handling
        self.error_handler = ErrorHandler()
        self.fallback_handler = FallbackHandler()
        self.graceful_degradation = GracefulDegradation()
        
        # Initialize Phase 2 components
        self.preference_parser = PreferenceParser()
        self.filter_engine = FilterEngine()
        self.ranker_v1 = RankerV1()
        
        # Initialize Phase 3 pipeline with Groq
        self.phase3_config = create_phase3_config_with_groq(
            groq_api_key=config.groq_api_key,
            model_name="llama3-8b-8192",
            max_tokens=1500,
            temperature=0.7
        )
        self.phase3_pipeline = Phase3Pipeline(self.phase3_config)
        
        # Load restaurant data
        self.restaurants_data = self._load_restaurant_data()
        
        # Initialize Phase 4 components
        self.api_server = RecommendationAPI(
            groq_api_key=config.groq_api_key,
            data_path=config.data_path
        )
        
        self.presentation_layer = PresentationLayer(
            api_base_url=f"http://{config.api_host}:{config.api_port}"
        )
        
        self.cli_interface = CLIInterface(
            api_base_url=f"http://{config.api_host}:{config.api_port}"
        )
        
        self.logger.info("Phase 4 application initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_restaurant_data(self) -> List[Dict[str, Any]]:
        """Load restaurant data from file."""
        try:
            import pandas as pd
            df = pd.read_csv(self.config.data_path)
            self.logger.info(f"Loaded {len(df)} restaurants from {self.config.data_path}")
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Failed to load restaurant data: {e}")
            return []
    
    def generate_recommendations_complete(
        self,
        user_preferences: Dict[str, Any],
        response_type: str = "recommendation",
        max_recommendations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate recommendations using the complete pipeline.
        
        Args:
            user_preferences: User preference dictionary
            response_type: Type of response (recommendation, ranking, explanation)
            max_recommendations: Maximum recommendations to return
            
        Returns:
            Complete recommendation response
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Parse preferences (Phase 2)
            self.logger.info("Parsing user preferences")
            parsed_preferences = self.preference_parser.parse_preferences(user_preferences)
            
            # Step 2: Filter candidates (Phase 2)
            self.logger.info("Filtering restaurant candidates")
            candidates = self.filter_engine.filter_restaurants(
                self.restaurants_data, parsed_preferences
            )
            
            if not candidates:
                self.logger.warning("No candidates found, using fallback")
                return self.fallback_handler.handle_no_matches(parsed_preferences)
            
            # Step 3: Generate AI recommendations (Phase 3)
            self.logger.info(f"Generating {response_type} with {len(candidates)} candidates")
            max_recs = max_recommendations or self.config.max_recommendations
            
            if response_type == "recommendation":
                result = self.phase3_pipeline.generate_recommendations(
                    candidates[:max_recs],
                    parsed_preferences
                )
            elif response_type == "ranking":
                result = self.phase3_pipeline.generate_ranking(
                    candidates[:max_recs],
                    parsed_preferences
                )
            elif response_type == "explanation":
                result = self.phase3_pipeline.generate_explanations(
                    candidates[:max_recs],
                    parsed_preferences
                )
            else:
                raise ValueError(f"Unknown response type: {response_type}")
            
            # Add pipeline metadata
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result.update({
                "pipeline_metadata": {
                    "total_candidates": len(candidates),
                    "candidates_used": min(len(candidates), max_recs),
                    "response_time_ms": int(response_time),
                    "pipeline_version": "phase4",
                    "groq_model": self.phase3_config.model_name
                }
            })
            
            self.logger.info(f"Recommendations generated in {response_time:.0f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return self.graceful_degradation.handle_request_failure(e, user_preferences)
    
    def run_api_server(self, debug: bool = False):
        """Run the API server."""
        self.logger.info(f"Starting API server on {self.config.api_host}:{self.config.api_port}")
        try:
            self.api_server.run(
                host=self.config.api_host,
                port=self.config.api_port,
                debug=debug
            )
        except Exception as e:
            self.logger.error(f"API server failed: {e}")
            raise
    
    def run_streamlit_app(self):
        """Run the Streamlit web application."""
        self.logger.info(f"Starting Streamlit app on {self.config.streamlit_host}:{self.config.streamlit_port}")
        try:
            import subprocess
            import sys
            
            # Run streamlit in subprocess
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "phase4.presentation_layer:create_streamlit_app",
                f"--server.port={self.config.streamlit_port}",
                f"--server.address={self.config.streamlit_host}"
            ]
            
            subprocess.run(cmd, check=True)
            
        except Exception as e:
            self.logger.error(f"Streamlit app failed: {e}")
            raise
    
    def run_cli(self, args: Optional[List[str]] = None):
        """Run the CLI interface."""
        self.logger.info("Starting CLI interface")
        try:
            import sys
            if args:
                sys.argv = ["cli_interface"] + args
            self.cli_interface.main()
        except Exception as e:
            self.logger.error(f"CLI interface failed: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Test Groq connection
            groq_status = self.phase3_pipeline.llm_client.test_connection()
            
            # Check data
            data_status = {
                "restaurants_loaded": len(self.restaurants_data),
                "data_path": self.config.data_path
            }
            
            # API status
            api_status = {
                "configured": True,
                "url": f"http://{self.config.api_host}:{self.config.api_port}"
            }
            
            return {
                "status": "operational" if groq_status else "degraded",
                "components": {
                    "groq_llm": {"status": "online" if groq_status else "offline"},
                    "phase2_pipeline": {"status": "online"},
                    "phase3_pipeline": {"status": "online"},
                    "api_server": api_status,
                    "data": data_status
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_components(self):
        """Run all components concurrently."""
        self.logger.info("Starting all Phase 4 components")
        
        try:
            # Create event loop for concurrent execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_components():
                """Run components concurrently."""
                # Start API server in background
                api_task = asyncio.create_task(
                    asyncio.to_thread(self.run_api_server)
                )
                
                # Wait a moment for API to start
                await asyncio.sleep(2)
                
                # Start Streamlit app
                streamlit_task = asyncio.create_task(
                    asyncio.to_thread(self.run_streamlit_app)
                )
                
                # Wait for both tasks (they run indefinitely)
                await asyncio.gather(api_task, streamlit_task, return_exceptions=True)
            
            # Run the components
            loop.run_until_complete(run_components())
            
        except KeyboardInterrupt:
            self.logger.info("Shutting down components")
        except Exception as e:
            self.logger.error(f"Component execution failed: {e}")
            raise
        finally:
            loop.close()
    
    def test_end_to_end(self) -> bool:
        """Test end-to-end functionality."""
        self.logger.info("Running end-to-end test")
        
        try:
            # Test data loading
            if not self.restaurants_data:
                self.logger.error("No restaurant data loaded")
                return False
            
            # Test preferences parsing
            test_preferences = {
                "location": "Downtown",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "max_cost_for_two": 1000
            }
            
            parsed = self.preference_parser.parse_preferences(test_preferences)
            if not parsed:
                self.logger.error("Preference parsing failed")
                return False
            
            # Test filtering
            candidates = self.filter_engine.filter_restaurants(
                self.restaurants_data, parsed
            )
            if not candidates:
                self.logger.warning("No candidates found for test (may be expected)")
            
            # Test Phase 3 pipeline
            if candidates:
                result = self.phase3_pipeline.generate_recommendations(
                    candidates[:2], parsed  # Use minimal candidates for test
                )
                if not result:
                    self.logger.error("Phase 3 pipeline failed")
                    return False
            
            # Test complete pipeline
            complete_result = self.generate_recommendations_complete(test_preferences)
            if not complete_result:
                self.logger.error("Complete pipeline failed")
                return False
            
            self.logger.info("End-to-end test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"End-to-end test failed: {e}")
            return False


def create_phase4_app(
    groq_api_key: str,
    data_path: str = "data/processed/restaurants.csv",
    **kwargs
) -> Phase4App:
    """
    Create Phase 4 application instance.
    
    Args:
        groq_api_key: Groq API key
        data_path: Path to restaurant data
        **kwargs: Additional configuration parameters
        
    Returns:
        Phase4App instance
    """
    config = Phase4Config(
        groq_api_key=groq_api_key,
        data_path=data_path,
        **kwargs
    )
    
    return Phase4App(config)


if __name__ == "__main__":
    import os
    
    # Get API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        exit(1)
    
    # Create and run application
    app = create_phase4_app(groq_api_key)
    
    # Test first
    if app.test_end_to_end():
        print("✅ End-to-end test passed")
        
        # Run API server
        app.run_api_server(debug=True)
    else:
        print("❌ End-to-end test failed")
        exit(1)
