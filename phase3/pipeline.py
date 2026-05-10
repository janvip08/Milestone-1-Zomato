"""Phase 3 Pipeline: Orchestrates LLM-based recommendation generation."""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

from .candidate_builder import CandidateBuilder
from .prompt_builder import PromptBuilder
from .llm_client import LLMClient, LLMConfig
from .response_parser import ResponseParser


@dataclass
class Phase3Config:
    """Configuration for Phase 3 pipeline."""
    llm_config: LLMConfig
    max_candidates: int = 10
    prompt_template: str = "recommendation"
    system_persona: str = "restaurant expert"
    enable_retry: bool = True
    validate_responses: bool = True


class Phase3Pipeline:
    """Main pipeline for Phase 3 LLM-based recommendations."""
    
    def __init__(self, config: Phase3Config):
        """
        Initialize the Phase 3 pipeline.
        
        Args:
            config: Configuration for the pipeline
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.candidate_builder = CandidateBuilder(max_candidates=config.max_candidates)
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient(config.llm_config)
        self.response_parser = ResponseParser()
        
        self.logger.info("Phase 3 pipeline initialized")
    
    def generate_recommendations(
        self,
        candidates: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM-based recommendations from filtered candidates.
        
        Args:
            candidates: List of restaurant candidates from Phase 2
            user_preferences: User preference dictionary
            additional_instructions: Optional custom instructions
            
        Returns:
            Structured recommendation response
        """
        try:
            # Step 1: Build context from candidates
            self.logger.info("Building candidate context")
            context = self.candidate_builder.build_context(candidates, user_preferences)
            
            # Step 2: Build prompt
            self.logger.info("Building prompt")
            system_prompt = self.prompt_builder.build_system_prompt(
                persona=self.config.system_persona
            )
            
            user_prompt = self.prompt_builder.build_prompt(
                context=context,
                template_type=self.config.prompt_template,
                additional_instructions=additional_instructions
            )
            
            # Step 3: Generate LLM response
            self.logger.info("Generating LLM response")
            llm_response = self.llm_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                use_retry=self.config.enable_retry
            )
            
            # Step 4: Parse response
            self.logger.info("Parsing LLM response")
            parsed_response = self.response_parser.parse_response(
                response_text=llm_response,
                response_type=self.config.prompt_template
            )
            
            # Step 5: Validate response
            if self.config.validate_responses:
                is_valid = self.response_parser.validate_response_structure(
                    parsed_response, self.config.prompt_template
                )
                if not is_valid:
                    self.logger.warning("Response validation failed")
            
            # Add metadata
            parsed_response["metadata"] = {
                "pipeline_version": "phase3",
                "total_candidates_processed": len(candidates),
                "candidates_used": min(len(candidates), self.config.max_candidates),
                "llm_provider": self.config.llm_config.provider,
                "model_name": self.config.llm_config.model_name,
                "prompt_template": self.config.prompt_template,
                "generated_at": self._get_timestamp()
            }
            
            self.logger.info("Recommendations generated successfully")
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise
    
    def generate_ranking(
        self,
        candidates: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ranking-focused analysis.
        
        Args:
            candidates: List of restaurant candidates from Phase 2
            user_preferences: User preference dictionary
            additional_instructions: Optional custom instructions
            
        Returns:
            Structured ranking response
        """
        # Temporarily switch to ranking template
        original_template = self.config.prompt_template
        self.config.prompt_template = "ranking"
        
        try:
            result = self.generate_recommendations(
                candidates, user_preferences, additional_instructions
            )
            return result
        finally:
            # Restore original template
            self.config.prompt_template = original_template
    
    def generate_explanations(
        self,
        candidates: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed explanations for recommendations.
        
        Args:
            candidates: List of restaurant candidates from Phase 2
            user_preferences: User preference dictionary
            additional_instructions: Optional custom instructions
            
        Returns:
            Structured explanation response
        """
        # Temporarily switch to explanation template
        original_template = self.config.prompt_template
        self.config.prompt_template = "explanation"
        
        try:
            result = self.generate_recommendations(
                candidates, user_preferences, additional_instructions
            )
            return result
        finally:
            # Restore original template
            self.config.prompt_template = original_template
    
    def format_for_display(self, response_data: Dict[str, Any]) -> str:
        """
        Format response data for user display.
        
        Args:
            response_data: Parsed response data
            
        Returns:
            Formatted string for display
        """
        response_type = response_data.get("metadata", {}).get("prompt_template", "recommendation")
        return self.response_parser.format_for_display(response_data, response_type)
    
    def test_pipeline(
        self, 
        sample_candidates: List[Dict[str, Any]], 
        sample_preferences: Dict[str, Any]
    ) -> bool:
        """
        Test the pipeline with sample data.
        
        Args:
            sample_candidates: Sample restaurant candidates
            sample_preferences: Sample user preferences
            
        Returns:
            True if test passes, False otherwise
        """
        try:
            self.logger.info("Testing pipeline with sample data")
            
            # Test candidate building
            context = self.candidate_builder.build_context(
                sample_candidates, sample_preferences
            )
            assert "candidates" in context
            assert "user_preferences" in context
            
            # Test prompt building
            prompt = self.prompt_builder.build_prompt(context)
            assert len(prompt) > 0
            
            # Test LLM connection
            connection_ok = self.llm_client.test_connection()
            if not connection_ok:
                self.logger.warning("LLM connection test failed")
                return False
            
            # Test full pipeline (with minimal candidates to save tokens)
            minimal_candidates = sample_candidates[:2] if len(sample_candidates) > 2 else sample_candidates
            result = self.generate_recommendations(minimal_candidates, sample_preferences)
            
            # Validate result structure
            assert "recommendations" in result or "ranked_restaurants" in result or "detailed_explanations" in result
            assert "metadata" in result
            
            self.logger.info("Pipeline test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline test failed: {e}")
            return False
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration."""
        return {
            "pipeline_version": "phase3",
            "components": {
                "candidate_builder": {
                    "max_candidates": self.config.max_candidates
                },
                "prompt_builder": {
                    "available_templates": self.prompt_builder.get_template_names(),
                    "current_template": self.config.prompt_template,
                    "system_persona": self.config.system_persona
                },
                "llm_client": self.llm_client.get_model_info(),
                "response_parser": {
                    "validation_enabled": self.config.validate_responses
                }
            },
            "settings": {
                "enable_retry": self.config.enable_retry,
                "validate_responses": self.config.validate_responses
            }
        }
    
    def update_config(self, **kwargs) -> None:
        """Update pipeline configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Updated config: {key} = {value}")
            else:
                self.logger.warning(f"Unknown config parameter: {key}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_sample_data(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Create sample data for testing."""
        sample_candidates = [
            {
                "name": "Italian Paradise",
                "cuisine": "Italian",
                "rating": 4.5,
                "cost_for_two": 800,
                "location": "Downtown",
                "delivery": True,
                "takeaway": True
            },
            {
                "name": "Spice Garden",
                "cuisine": "Indian",
                "rating": 4.2,
                "cost_for_two": 600,
                "location": "Downtown",
                "delivery": False,
                "takeaway": True
            },
            {
                "name": "Sushi Master",
                "cuisine": "Japanese",
                "rating": 4.8,
                "cost_for_two": 1200,
                "location": "Downtown",
                "delivery": True,
                "takeaway": False
            }
        ]
        
        sample_preferences = {
            "location": "Downtown",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "max_cost_for_two": 1000,
            "budget_category": "moderate"
        }
        
        return sample_candidates, sample_preferences


def create_default_config(
    provider: str = "openai",
    model_name: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    **kwargs
) -> Phase3Config:
    """
    Create a default configuration for Phase 3 pipeline.
    
    Args:
        provider: LLM provider name
        model_name: Model name to use
        api_key: API key for the provider
        **kwargs: Additional configuration parameters
        
    Returns:
        Phase3Config object
    """
    llm_config = LLMConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        **kwargs
    )
    
    return Phase3Config(llm_config=llm_config)
