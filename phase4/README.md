# Phase 4: Application Layer and UI Delivery

This phase delivers restaurant recommendations through a complete user-facing interface, integrating all previous phases into an end-to-end application powered by Groq LLM.

## Overview

Phase 4 provides multiple interfaces for users to get AI-powered restaurant recommendations:

- **REST API**: FastAPI-based server for programmatic access
- **Web UI**: Streamlit-based interactive web interface  
- **CLI**: Command-line interface for power users
- **Error Handling**: Comprehensive fallback mechanisms

## Architecture

### Core Components

#### 1. GroqProvider (`groq_provider.py`)
Fast LLM inference using Groq API with optimized models.

**Key Features:**
- Support for multiple Groq models (Llama 3, Mixtral, Gemma)
- Fast inference with low latency
- Automatic retry and error handling
- Connection testing and health checks

**Supported Models:**
- `llama-3.1-8b-instant`: Llama 3.1 8B (Fast inference)
- `llama3-70b-8192`: Llama 3 70B (8K context)  
- `mixtral-8x7b-32768`: Mixtral 8x7B (32K context)
- `gemma-7b-it`: Gemma 7B (Instruction Tuned)

#### 2. RecommendationAPI (`api_server.py`)
FastAPI-based REST API server.

**Endpoints:**
- `POST /recommend`: Generate recommendations
- `GET /restaurants`: List restaurants with filtering
- `GET /health`: System health check
- `GET /models`: Available LLM models
- `POST /feedback`: Submit feedback

**Features:**
- Automatic request validation
- Comprehensive error handling
- Response time tracking
- CORS support for web integration

#### 3. PresentationLayer (`presentation_layer.py`)
Streamlit-based web interface.

**Features:**
- Interactive preference forms
- Real-time recommendation display
- AI explanations and match scores
- Responsive design
- Sample recommendations for demo

#### 4. CLIInterface (`cli_interface.py`)
Command-line interface for recommendations.

**Features:**
- Interactive mode with guided input
- Single command mode with arguments
- JSON output option
- API status checking
- Comprehensive help system

#### 5. ErrorHandler & FallbackHandler (`error_handler.py`)
Robust error handling and graceful degradation.

**Features:**
- Categorized error responses
- Location-based fallback recommendations
- Rule-based ranking when LLM fails
- User-friendly error messages
- System status monitoring

#### 6. Phase4App (`app_orchestrator.py`)
Main application orchestrator.

**Features:**
- End-to-end pipeline coordination
- Component lifecycle management
- System health monitoring
- Concurrent component execution
- Comprehensive testing

## Installation and Setup

### Prerequisites

1. **Python 3.8+**
2. **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
3. **Restaurant Data**: Processed dataset from Phase 1

### Dependencies

```bash
pip install -r phase4/requirements.txt
```

### Environment Setup

```bash
# Set Groq API key
export GROQ_API_KEY="your-groq-api-key"

# Optional: Set data path
export RESTAURANT_DATA_PATH="data/processed/restaurants.csv"
```

### Quick Start

```python
from phase4 import create_phase4_app

# Create app with Groq
app = create_phase4_app(groq_api_key="your-api-key")

# Generate recommendations
preferences = {
    "location": "Downtown",
    "cuisine": "Italian", 
    "min_rating": 4.0,
    "max_cost_for_two": 1000
}

result = app.generate_recommendations_complete(preferences)
print(result["recommendations"])
```

## Usage Examples

### 1. API Server

```bash
# Start the API server
python -m phase4.main api-server

# Or run directly
python -m phase4.api_server
```

The API will be available at:
- **Server**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Web Interface

```bash
# Start Streamlit app (requires API server running)
python -m phase4.main streamlit

# Or run directly
streamlit run phase4/presentation_layer.py
```

The web interface will be available at http://localhost:8501

### 3. Command Line Interface

```bash
# Interactive mode
python -m phase4.main cli

# Single command
python -m phase4.main --location Downtown --cuisine Italian --max-cost 1000

# JSON output
python -m phase4.main --location Downtown --output json

# Check API status
python -m phase4.main --status
```

### 4. Programmatic Usage

```python
from phase4 import create_phase4_app

# Initialize app
app = create_phase4_app(groq_api_key="your-key")

# Get recommendations
result = app.generate_recommendations_complete(
    preferences={
        "location": "Downtown",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "max_cost_for_two": 1000,
        "occasion": "date night"
    },
    response_type="recommendation",
    max_recommendations=5
)

# Access results
recommendations = result["recommendations"]
metadata = result["pipeline_metadata"]
```

## API Reference

### Recommendation Request

```json
{
    "preferences": {
        "location": "Downtown",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "max_cost_for_two": 1000,
        "meal_type": "dinner",
        "occasion": "date night",
        "additional_requirements": "Outdoor seating"
    },
    "max_recommendations": 5,
    "response_type": "recommendation",
    "include_explanations": true
}
```

### Recommendation Response

```json
{
    "recommendations": [
        {
            "rank": 1,
            "restaurant_name": "Bella Italia",
            "match_score": 0.95,
            "reasons": [
                "Perfect Italian cuisine match",
                "Excellent rating of 4.5",
                "Great ambiance for date night"
            ],
            "highlights": ["Authentic pasta", "Wine selection"],
            "price_indication": "Moderate",
            "best_for": "Date Night"
        }
    ],
    "summary": "Found 3 great Italian restaurants in Downtown",
    "total_matches": 3,
    "response_time_ms": 850,
    "pipeline_metadata": {
        "total_candidates": 15,
        "candidates_used": 5,
        "groq_model": "llama3-8b-8192"
    }
}
```

## Configuration

### Phase4Config

```python
from phase4 import Phase4Config, create_phase4_app

config = Phase4Config(
    groq_api_key="your-api-key",
    data_path="data/processed/restaurants.csv",
    api_host="0.0.0.0",
    api_port=8000,
    streamlit_port=8501,
    max_recommendations=10,
    response_timeout=30
)

app = create_phase4_app(config=config)
```

### Groq Configuration

```python
from phase4.groq_provider import create_groq_config

config = create_groq_config(
    api_key="your-api-key",
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=1500
)
```

## Error Handling

The system includes comprehensive error handling:

### Error Categories

1. **Connection Errors**: API connectivity issues
2. **Timeout Errors**: Request timeouts
3. **Validation Errors**: Invalid input parameters
4. **LLM Errors**: Model inference failures
5. **Data Errors**: Restaurant data issues

### Fallback Strategies

1. **Rule-based Ranking**: When LLM fails
2. **Location-based Suggestions**: When no matches found
3. **Generic Recommendations**: When all else fails
4. **Graceful Degradation**: Maintain functionality

### Error Response Format

```json
{
    "error": "ConnectionError",
    "message": "Unable to connect to AI service",
    "user_friendly": "Our AI service is temporarily unavailable",
    "status_code": 503,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Testing

### End-to-End Test

```bash
python -m phase4.main test
```

### Component Tests

```bash
# Test Groq provider
python -m phase4.main groq-example

# Test API usage
python -m phase4.main api-example

# Check system status
python -m phase4.main status
```

### Manual Testing

```python
from phase4 import create_phase4_app

app = create_phase4_app(groq_api_key="your-key")
success = app.test_end_to_end()
print(f"Test passed: {success}")
```

## Performance

### Response Times

- **API Response**: < 1 second (typical)
- **Groq Inference**: ~500ms for Llama 3 8B
- **Complete Pipeline**: < 2 seconds

### Optimization Tips

1. **Model Selection**: Use `llama-3.1-8b-instant` for fastest response
2. **Candidate Limiting**: Reduce `max_recommendations` for faster processing
3. **Caching**: Enable response caching for repeated queries
4. **Batch Processing**: Process multiple requests in parallel

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### System Status

```python
app = create_phase4_app(groq_api_key="your-key")
status = app.get_system_status()
print(status)
```

### Metrics Tracked

- Response times
- Error rates
- API usage
- Model performance
- System health

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "phase4.api_server"]
```

### Environment Variables

```bash
GROQ_API_KEY=your-api-key
RESTAURANT_DATA_PATH=/app/data/processed/restaurants.csv
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Production Considerations

1. **API Rate Limiting**: Implement rate limiting
2. **Authentication**: Add API key authentication
3. **Monitoring**: Set up health checks and alerting
4. **Scaling**: Load balance multiple API instances
5. **Security**: Input validation and sanitization

## Integration with Other Phases

### Input from Phase 2
- Filtered restaurant candidates
- User preference parsing
- Rule-based ranking fallback

### Input from Phase 3
- LLM-based recommendation generation
- Prompt templates and response parsing
- Structured JSON output

### Output for Phase 5
- User feedback collection
- Performance metrics
- Usage analytics
- Error tracking

## Troubleshooting

### Common Issues

1. **Groq API Key Error**
   ```bash
   export GROQ_API_KEY="your-api-key"
   ```

2. **API Server Not Running**
   ```bash
   python -m phase4.main api-server
   ```

3. **No Restaurant Data**
   ```bash
   export RESTAURANT_DATA_PATH="path/to/restaurants.csv"
   ```

4. **Connection Timeout**
   - Check network connectivity
   - Increase timeout in configuration

### Debug Mode

```bash
python -m phase4.main api-server --log-level DEBUG
```

### Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **User Profiles**: Personal recommendations based on history
2. **Multi-city Support**: Expand to multiple locations
3. **Real-time Updates**: Live restaurant data integration
4. **Advanced Filtering**: More sophisticated preference options
5. **Mobile App**: Native mobile application
6. **Social Features**: Reviews, ratings, and sharing

## Contributing

When contributing to Phase 4:

1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Handle errors gracefully
5. Consider performance implications
6. Test with different Groq models

## License

This phase is part of the restaurant recommendation system project.
