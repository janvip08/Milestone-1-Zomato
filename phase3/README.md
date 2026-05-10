# Phase 3: LLM Integration and Recommendation Logic

This phase implements the LLM-based recommendation system that adds intelligence and personalization to the restaurant recommendation pipeline.

## Overview

Phase 3 takes the filtered restaurant candidates from Phase 2 and uses Large Language Models (LLMs) to:
- Generate personalized recommendations with explanations
- Rank restaurants based on nuanced criteria
- Provide detailed reasoning for recommendations
- Format responses in structured JSON for easy consumption

## Architecture

### Core Components

#### 1. CandidateBuilder (`candidate_builder.py`)
Formats filtered restaurant data into structured context for LLM processing.

**Key Features:**
- Limits candidates to configurable maximum (default: 10)
- Formats ratings, costs, and cuisine types for readability
- Extracts highlights from restaurant data
- Builds comprehensive context with user preferences

**Usage:**
```python
from phase3 import CandidateBuilder

builder = CandidateBuilder(max_candidates=10)
context = builder.build_context(candidates, user_preferences)
```

#### 2. PromptBuilder (`prompt_builder.py`)
Manages prompt templates and builds structured prompts for LLMs.

**Key Features:**
- Multiple prompt templates (recommendation, ranking, explanation)
- Configurable system prompts with different personas
- Template validation and custom template support
- Few-shot examples for better LLM performance

**Available Templates:**
- `recommendation`: Main recommendation generation
- `ranking`: Focused ranking analysis
- `explanation`: Detailed explanations

**Usage:**
```python
from phase3 import PromptBuilder

builder = PromptBuilder()
prompt = builder.build_prompt(
    context=context,
    template_type="recommendation",
    additional_instructions="Focus on romantic atmosphere"
)
```

#### 3. LLMClient (`llm_client.py`)
Handles integration with various LLM providers with robust error handling.

**Supported Providers:**
- OpenAI (GPT models)
- Anthropic (Claude models)
- Local models (Ollama, etc.)

**Key Features:**
- Retry logic with exponential backoff
- Structured JSON response generation
- Connection testing
- Configuration management

**Usage:**
```python
from phase3 import LLMClient, LLMConfig

config = LLMConfig(
    provider="openai",
    model_name="gpt-3.5-turbo",
    api_key="your-api-key"
)
client = LLMClient(config)
response = client.generate_response(prompt, system_prompt)
```

#### 4. ResponseParser (`response_parser.py`)
Parses and validates LLM responses into structured data.

**Key Features:**
- JSON extraction from markdown or plain text
- Schema validation for different response types
- Data structure validation and cleaning
- Formatted output for display

**Usage:**
```python
from phase3 import ResponseParser

parser = ResponseParser()
parsed_data = parser.parse_response(llm_response, "recommendation")
```

#### 5. Phase3Pipeline (`pipeline.py`)
Main orchestrator that coordinates all components.

**Key Features:**
- End-to-end recommendation generation
- Multiple response types (recommendations, ranking, explanations)
- Pipeline testing and validation
- Configuration management

**Usage:**
```python
from phase3 import Phase3Pipeline, create_default_config

config = create_default_config(provider="openai", api_key="your-key")
pipeline = Phase3Pipeline(config)

result = pipeline.generate_recommendations(candidates, preferences)
print(pipeline.format_for_display(result))
```

## Installation and Setup

### Dependencies

```bash
pip install requests
```

### Environment Variables

For different providers, set these environment variables:

**OpenAI:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**Anthropic:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

**Local Models:**
```bash
# Make sure Ollama is running
ollama serve
```

### Quick Start

```python
from phase3 import Phase3Pipeline, create_default_config

# Setup configuration
config = create_default_config(
    provider="openai",
    model_name="gpt-3.5-turbo",
    api_key="your-api-key"
)

# Initialize pipeline
pipeline = Phase3Pipeline(config)

# Sample data
candidates = [
    {
        "name": "Italian Paradise",
        "cuisine": "Italian",
        "rating": 4.5,
        "cost_for_two": 800,
        "location": "Downtown"
    }
]

preferences = {
    "location": "Downtown",
    "cuisine": "Italian",
    "min_rating": 4.0,
    "max_cost_for_two": 1000
}

# Generate recommendations
result = pipeline.generate_recommendations(candidates, preferences)
print(pipeline.format_for_display(result))
```

## Configuration

### LLMConfig

```python
LLMConfig(
    provider="openai",           # LLM provider
    model_name="gpt-3.5-turbo",  # Model name
    api_key="your-key",          # API key (if required)
    api_base=None,               # Custom API base URL
    max_tokens=2000,             # Maximum tokens in response
    temperature=0.7,             # Response randomness
    timeout=30,                  # Request timeout
    retry_attempts=3,            # Number of retry attempts
    retry_delay=1.0             # Initial retry delay
)
```

### Phase3Config

```python
Phase3Config(
    llm_config=llm_config,       # LLM configuration
    max_candidates=10,           # Maximum candidates to process
    prompt_template="recommendation",  # Default template
    system_persona="restaurant expert",  # System persona
    enable_retry=True,           # Enable retry logic
    validate_responses=True      # Validate response structure
)
```

## Response Formats

### Recommendation Response

```json
{
    "recommendations": [
        {
            "rank": 1,
            "restaurant_name": "Restaurant Name",
            "match_score": 0.95,
            "reasons": [
                "Perfect match for Italian cuisine preference",
                "Excellent rating of 4.5+",
                "Great value within budget"
            ],
            "highlights": [
                "Known for authentic flavors",
                "Popular among locals"
            ],
            "price_indication": "Moderate",
            "best_for": "Date night"
        }
    ],
    "summary": "Brief summary of recommendations",
    "alternative_suggestions": "If none work, consider...",
    "total_matches": 5,
    "metadata": {
        "pipeline_version": "phase3",
        "generated_at": "2024-01-01T12:00:00"
    }
}
```

### Ranking Response

```json
{
    "ranked_restaurants": [
        {
            "original_rank": 3,
            "new_rank": 1,
            "restaurant_name": "Restaurant Name",
            "score_breakdown": {
                "cuisine_match": 0.9,
                "rating": 0.8,
                "price": 0.7,
                "location": 0.8
            },
            "overall_score": 0.81,
            "ranking_reason": "Why this moved to position 1"
        }
    ],
    "ranking_methodology": "Explanation of ranking approach"
}
```

## Examples

### Basic Usage

```python
# See main.py for complete examples
python -m phase3.main
```

### Testing

```python
# Run tests
python -m phase3.test_phase3

# Or use unittest
python -m unittest phase3.test_phase3
```

### Pipeline Testing

```python
# Test pipeline with sample data
pipeline = Phase3Pipeline(config)
candidates, preferences = pipeline.create_sample_data()
test_passed = pipeline.test_pipeline(candidates, preferences)
```

## Error Handling

The system includes comprehensive error handling:

1. **LLM API Errors**: Automatic retry with exponential backoff
2. **JSON Parsing Errors**: Fallback extraction from text
3. **Validation Errors**: Clear error messages for missing fields
4. **Connection Errors**: Graceful degradation and logging

## Performance Considerations

1. **Candidate Limiting**: Process only top N candidates to save tokens
2. **Caching**: Consider caching responses for repeated queries
3. **Batch Processing**: Process multiple requests in parallel where possible
4. **Token Management**: Monitor token usage to control costs

## Integration with Other Phases

### Input from Phase 2
Phase 3 expects:
- List of restaurant dictionaries with fields: name, cuisine, rating, cost_for_two, location
- User preference dictionary with filtering criteria

### Output for Phase 4
Phase 3 provides:
- Structured recommendation data in JSON format
- Formatted display strings
- Metadata about the generation process

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure environment variables are set correctly
2. **Connection Errors**: Check network connectivity and API endpoints
3. **JSON Parsing Errors**: Verify LLM is responding with valid JSON
4. **Empty Responses**: Check prompt templates and system instructions

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
pipeline = Phase3Pipeline(config)
```

## Future Enhancements

1. **Vector Search Integration**: Combine with semantic search
2. **User Profiles**: Personalization based on history
3. **Multi-turn Conversations**: Interactive refinement
4. **A/B Testing**: Compare different prompt strategies
5. **Cost Optimization**: Smart token usage and caching

## Contributing

When extending Phase 3:

1. Follow the existing component structure
2. Add comprehensive tests for new features
3. Update documentation and examples
4. Consider backward compatibility
5. Add proper error handling and logging

## License

This phase is part of the larger restaurant recommendation system project.
