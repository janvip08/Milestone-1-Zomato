"""LLM Client: Handles API integration with various LLM providers."""

from typing import Dict, Any, Optional, List
import json
import time
import logging
from abc import ABC, abstractmethod
import requests
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    provider: str  # "openai", "anthropic", "local", etc.
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from LLM."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://api.openai.com/v1"
        
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using OpenAI API."""
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
            raise Exception(f"OpenAI API request failed: {e}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://api.anthropic.com"
        
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Anthropic API."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Combine system prompt and user prompt for Claude
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        data = {
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": full_prompt}]
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/messages",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Anthropic API request failed: {e}")


class LocalProvider(LLMProvider):
    """Local LLM provider (Ollama, etc.)."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_base = config.api_base or "http://localhost:11434"
        
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using local LLM API."""
        headers = {"Content-Type": "application/json"}
        
        # Combine prompts for local models
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        data = {
            "model": self.config.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Local LLM API request failed: {e}")


class GroqProvider(LLMProvider):
    """Groq API provider."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://api.groq.com/openai/v1"
        
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Groq API."""
        import requests
        import ssl
        import certifi
        import os
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        try:
            # Try with proper SSL verification first (production-safe)
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout,
                verify=certifi.where()
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Groq API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.SSLError as ssl_error:
            # Fallback for local development SSL issues
            print(f"SSL verification failed, attempting fallback for local development...")
            try:
                # Try with SSL verification disabled (local development only)
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout,
                    verify=False
                )
                
                # Suppress SSL warning for local development
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Groq API error: {response.status_code} - {response.text}")
                    
            except Exception as fallback_error:
                raise Exception(f"Groq API SSL fallback failed: {fallback_error}")
                
        except Exception as e:
            raise Exception(f"Groq API request failed: {e}")


class LLMClient:
    """Main LLM client that handles different providers and error management."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM client with configuration.
        
        Args:
            config: LLM configuration object
        """
        self.config = config
        self.provider = self._create_provider(config)
        self.logger = logging.getLogger(__name__)
        
    def _create_provider(self, config: LLMConfig) -> LLMProvider:
        """Create appropriate provider based on configuration."""
        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "claude": AnthropicProvider,
            "local": LocalProvider,
            "ollama": LocalProvider,
            "groq": GroqProvider
        }
        
        provider_class = provider_map.get(config.provider.lower())
        if not provider_class:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        return provider_class(config)
    
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: str = "",
        use_retry: bool = True
    ) -> str:
        """
        Generate response from LLM with retry logic.
        
        Args:
            prompt: Main prompt for LLM
            system_prompt: Optional system prompt
            use_retry: Whether to use retry logic on failure
            
        Returns:
            LLM response string
        """
        if not use_retry:
            return self.provider.generate_response(prompt, system_prompt)
        
        last_exception = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.provider.generate_response(prompt, system_prompt)
                self.logger.info(f"LLM response generated successfully on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"LLM request failed on attempt {attempt + 1}: {e}")
                
                if attempt < self.config.retry_attempts - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        # All retries failed
        self.logger.error(f"LLM request failed after {self.config.retry_attempts} attempts")
        raise Exception(f"LLM generation failed: {last_exception}")
    
    def generate_structured_response(
        self, 
        prompt: str, 
        system_prompt: str = "",
        expected_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from LLM.
        
        Args:
            prompt: Main prompt for LLM
            system_prompt: Optional system prompt
            expected_schema: Optional schema for validation
            
        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction to system prompt
        json_instruction = "\n\nIMPORTANT: You must respond with valid JSON only. No markdown formatting, no explanations outside the JSON."
        enhanced_system_prompt = system_prompt + json_instruction
        
        response = self.generate_response(prompt, enhanced_system_prompt)
        
        # Try to parse JSON
        try:
            parsed_response = json.loads(response)
            
            # Validate against schema if provided
            if expected_schema:
                self._validate_schema(parsed_response, expected_schema)
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            json_response = self._extract_json_from_text(response)
            if json_response:
                return json_response
            
            raise Exception(f"Failed to parse JSON response: {e}")
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that might contain markdown or other content."""
        import re
        
        # Try to find JSON block in markdown
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in the text
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _validate_schema(self, response: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Basic schema validation (placeholder for full validation)."""
        # This is a simple validation - in production, use jsonschema
        required_keys = schema.get("required", [])
        
        for key in required_keys:
            if key not in response:
                raise ValueError(f"Missing required key in response: {key}")
    
    def test_connection(self) -> bool:
        """Test connection to LLM provider."""
        try:
            test_prompt = "Respond with 'OK' to confirm connection."
            response = self.generate_response(test_prompt, use_retry=False)
            return "OK" in response.upper()
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": self.config.provider,
            "model_name": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_base": self.config.api_base
        }
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown config parameter: {key}")
