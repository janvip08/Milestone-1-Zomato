"""Test cases for Phase 3 components."""

import unittest
from unittest.mock import Mock, patch
import json

from .candidate_builder import CandidateBuilder
from .prompt_builder import PromptBuilder
from .llm_client import LLMClient, LLMConfig, OpenAIProvider
from .response_parser import ResponseParser
from .pipeline import Phase3Pipeline, Phase3Config


class TestCandidateBuilder(unittest.TestCase):
    """Test cases for CandidateBuilder."""
    
    def setUp(self):
        self.builder = CandidateBuilder(max_candidates=3)
        self.sample_candidates = [
            {
                "name": "Test Restaurant",
                "cuisine": "Italian",
                "rating": 4.5,
                "cost_for_two": 800,
                "location": "Downtown"
            }
        ]
        self.sample_preferences = {
            "location": "Downtown",
            "cuisine": "Italian",
            "min_rating": 4.0
        }
    
    def test_build_context(self):
        """Test context building."""
        context = self.builder.build_context(self.sample_candidates, self.sample_preferences)
        
        self.assertIn("user_preferences", context)
        self.assertIn("candidates", context)
        self.assertIn("total_candidates", context)
        self.assertIn("context_summary", context)
        self.assertEqual(context["total_candidates"], 1)
    
    def test_format_cuisine(self):
        """Test cuisine formatting."""
        result = self.builder._format_cuisine("italian")
        self.assertEqual(result, "Italian")
        
        result = self.builder._format_cuisine("")
        self.assertEqual(result, "Various")
    
    def test_format_rating(self):
        """Test rating formatting."""
        result = self.builder._format_rating(4.5)
        self.assertEqual(result, "4.5/5.0")
        
        result = self.builder._format_rating("invalid")
        self.assertEqual(result, "Not rated")
    
    def test_format_cost(self):
        """Test cost formatting."""
        result = self.builder._format_cost(800)
        self.assertEqual(result, "₹800 for two")
        
        result = self.builder._format_cost(0)
        self.assertEqual(result, "Price not available")
    
    def test_validate_candidates(self):
        """Test candidate validation."""
        valid = self.builder.validate_candidates(self.sample_candidates)
        self.assertTrue(valid)
        
        invalid_candidates = [{"name": "Test"}]  # Missing required fields
        valid = self.builder.validate_candidates(invalid_candidates)
        self.assertFalse(valid)


class TestPromptBuilder(unittest.TestCase):
    """Test cases for PromptBuilder."""
    
    def setUp(self):
        self.builder = PromptBuilder()
        self.sample_context = {
            "user_preferences": {"cuisine": "Italian"},
            "candidates": [{"name": "Test Restaurant"}],
            "total_candidates": 1,
            "context_summary": "Test summary"
        }
    
    def test_build_prompt(self):
        """Test prompt building."""
        prompt = self.builder.build_prompt(self.sample_context)
        self.assertIn("User Preferences", prompt)
        self.assertIn("Available Restaurants", prompt)
        self.assertIn("Test Restaurant", prompt)
    
    def test_get_template_names(self):
        """Test getting template names."""
        names = self.builder.get_template_names()
        self.assertIn("recommendation", names)
        self.assertIn("ranking", names)
        self.assertIn("explanation", names)
    
    def test_build_system_prompt(self):
        """Test system prompt building."""
        prompt = self.builder.build_system_prompt()
        self.assertIn("restaurant recommendation expert", prompt)
        
        prompt = self.builder.build_system_prompt(persona="food critic")
        self.assertIn("food critic", prompt)
    
    def test_add_custom_template(self):
        """Test adding custom templates."""
        custom_template = "Custom template with {variable}"
        self.builder.add_custom_template("custom", custom_template)
        
        names = self.builder.get_template_names()
        self.assertIn("custom", names)


class TestResponseParser(unittest.TestCase):
    """Test cases for ResponseParser."""
    
    def setUp(self):
        self.parser = ResponseParser()
    
    def test_extract_json_valid(self):
        """Test extracting valid JSON."""
        json_text = '{"key": "value"}'
        result = self.parser._extract_json(json_text)
        self.assertEqual(result, {"key": "value"})
    
    def test_extract_json_from_markdown(self):
        """Test extracting JSON from markdown."""
        markdown_text = '```json\n{"key": "value"}\n```'
        result = self.parser._extract_json(markdown_text)
        self.assertEqual(result, {"key": "value"})
    
    def test_parse_recommendation_response(self):
        """Test parsing recommendation response."""
        response_data = {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_name": "Test Restaurant",
                    "match_score": 0.9,
                    "reasons": ["Good rating"],
                    "highlights": ["Cozy"],
                    "price_indication": "Moderate",
                    "best_for": "Dinner"
                }
            ],
            "summary": "Test summary"
        }
        
        result = self.parser.parse_recommendation_response(response_data)
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["restaurant_name"], "Test Restaurant")
    
    def test_validate_response_structure(self):
        """Test response validation."""
        valid_data = {"recommendations": []}
        is_valid = self.parser.validate_response_structure(valid_data, "recommendation")
        self.assertTrue(is_valid)
        
        invalid_data = {"wrong_key": []}
        is_valid = self.parser.validate_response_structure(invalid_data, "recommendation")
        self.assertFalse(is_valid)


class TestLLMClient(unittest.TestCase):
    """Test cases for LLMClient."""
    
    def setUp(self):
        self.config = LLMConfig(
            provider="openai",
            model_name="gpt-3.5-turbo",
            api_key="test-key"
        )
    
    @patch('requests.post')
    def test_openai_provider_success(self, mock_post):
        """Test successful OpenAI API call."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        provider = OpenAIProvider(self.config)
        result = provider.generate_response("Test prompt")
        self.assertEqual(result, "Test response")
    
    @patch('requests.post')
    def test_openai_provider_failure(self, mock_post):
        """Test failed OpenAI API call."""
        mock_post.side_effect = Exception("API Error")
        
        provider = OpenAIProvider(self.config)
        with self.assertRaises(Exception):
            provider.generate_response("Test prompt")
    
    def test_create_provider(self):
        """Test provider creation."""
        client = LLMClient(self.config)
        self.assertIsInstance(client.provider, OpenAIProvider)
    
    def test_unsupported_provider(self):
        """Test unsupported provider."""
        config = LLMConfig(provider="unsupported", model_name="test")
        with self.assertRaises(ValueError):
            LLMClient(config)


class TestPhase3Pipeline(unittest.TestCase):
    """Test cases for Phase3Pipeline."""
    
    def setUp(self):
        self.llm_config = LLMConfig(
            provider="openai",
            model_name="gpt-3.5-turbo",
            api_key="test-key"
        )
        self.config = Phase3Config(llm_config=self.llm_config)
        self.pipeline = Phase3Pipeline(self.config)
        
        self.sample_candidates = [
            {
                "name": "Test Restaurant",
                "cuisine": "Italian",
                "rating": 4.5,
                "cost_for_two": 800,
                "location": "Downtown"
            }
        ]
        
        self.sample_preferences = {
            "location": "Downtown",
            "cuisine": "Italian",
            "min_rating": 4.0
        }
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        self.assertIsNotNone(self.pipeline.candidate_builder)
        self.assertIsNotNone(self.pipeline.prompt_builder)
        self.assertIsNotNone(self.pipeline.llm_client)
        self.assertIsNotNone(self.pipeline.response_parser)
    
    def test_get_pipeline_info(self):
        """Test getting pipeline info."""
        info = self.pipeline.get_pipeline_info()
        self.assertIn("pipeline_version", info)
        self.assertIn("components", info)
        self.assertEqual(info["pipeline_version"], "phase3")
    
    def test_create_sample_data(self):
        """Test sample data creation."""
        candidates, preferences = self.pipeline.create_sample_data()
        self.assertIsInstance(candidates, list)
        self.assertIsInstance(preferences, dict)
        self.assertGreater(len(candidates), 0)
    
    def test_update_config(self):
        """Test config updates."""
        self.pipeline.update_config(max_candidates=5)
        self.assertEqual(self.pipeline.config.max_candidates, 5)
    
    @patch.object(LLMClient, 'generate_response')
    def test_generate_recommendations_mock(self, mock_generate):
        """Test recommendation generation with mocked LLM."""
        mock_generate.return_value = json.dumps({
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_name": "Test Restaurant",
                    "match_score": 0.9,
                    "reasons": ["Good match"],
                    "highlights": ["Nice place"],
                    "price_indication": "Moderate",
                    "best_for": "Dinner"
                }
            ],
            "summary": "Test summary",
            "total_matches": 1
        })
        
        result = self.pipeline.generate_recommendations(
            self.sample_candidates, 
            self.sample_preferences
        )
        
        self.assertIn("recommendations", result)
        self.assertIn("metadata", result)
        self.assertEqual(len(result["recommendations"]), 1)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestCandidateBuilder,
        TestPromptBuilder,
        TestResponseParser,
        TestLLMClient,
        TestPhase3Pipeline
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
