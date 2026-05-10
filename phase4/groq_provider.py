"""Groq LLM Provider: Fast LLM inference using Groq API."""

from typing import Dict, Any, Optional
import json
import time
import logging
import requests
from dataclasses import dataclass

from phase3.llm_client import LLMProvider, LLMConfig


@dataclass
class GroqConfig:
    """Configuration for Groq provider."""
    api_key: str
    model_name: str = "llama3-8b-8192"
    api_base: str = "https://api.groq.com/openai/v1"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class GroqProvider(LLMProvider):
    """Groq API provider for fast LLM inference."""
    
    def __init__(self, config: GroqConfig):
        """
        Initialize Groq provider.
        
        Args:
            config: Groq configuration object
        """
        self.config = config
        self.api_key = config.api_key
        self.api_base = config.api_base
        self.logger = logging.getLogger(__name__)
        
        # Available Groq models
        self.available_models = {
            "llama3-8b-8192": "Llama 3 8B (8K context)",
            "llama3-70b-8192": "Llama 3 70B (8K context)",
            "mixtral-8x7b-32768": "Mixtral 8x7B (32K context)",
            "gemma-7b-it": "Gemma 7B (Instruction Tuned)"
        }
        
        if config.model_name not in self.available_models:
            self.logger.warning(f"Unknown model: {config.model_name}. Available: {list(self.available_models.keys())}")
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate response using Groq API.
        
        Args:
            prompt: Main prompt for LLM
            system_prompt: Optional system prompt
            
        Returns:
            LLM response string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API request failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "groq",
            "model_name": self.config.model_name,
            "model_description": self.available_models.get(self.config.model_name, "Unknown"),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_base": self.config.api_base
        }
    
    def list_available_models(self) -> Dict[str, str]:
        """Get list of available models."""
        return self.available_models.copy()
    
    def test_connection(self) -> bool:
        """Test connection to Groq API."""
        try:
            test_prompt = "Respond with 'OK' to confirm connection."
            response = self.generate_response(test_prompt)
            return "OK" in response.upper()
        except Exception as e:
            self.logger.error(f"Groq connection test failed: {e}")
            return False


def create_groq_config(
    api_key: str,
    model_name: str = "llama3-8b-8192",
    **kwargs
) -> GroqConfig:
    """
    Create Groq configuration.
    
    Args:
        api_key: Groq API key
        model_name: Model name to use
        **kwargs: Additional configuration parameters
        
    Returns:
        GroqConfig object
    """
    return GroqConfig(
        api_key=api_key,
        model_name=model_name,
        **kwargs
    )


def create_phase3_config_with_groq(
    groq_api_key: str,
    model_name: str = "llama3-8b-8192",
    **kwargs
) -> LLMConfig:
    """
    Create Phase 3 LLMConfig with Groq provider.
    
    Args:
        groq_api_key: Groq API key
        model_name: Model name to use
        **kwargs: Additional configuration parameters
        
    Returns:
        LLMConfig object compatible with Phase 3
    """
    return LLMConfig(
        provider="groq",
        model_name=model_name,
        api_key=groq_api_key,
        **kwargs
    )
