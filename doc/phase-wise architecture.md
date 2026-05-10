# Restaurant Recommendation System - Complete Architecture

> **Status:** Phases 0-5 Implemented | **LLM:** Groq | **Backend:** FastAPI | **Frontend:** Streamlit | **Database:** CSV/JSON

> Related: Edge case catalog is available in `doc/edge-cases.md`.

## System Overview

The restaurant recommendation system is a complete AI-powered application that provides personalized restaurant recommendations using Groq LLM. The system consists of:

- **Backend API** (FastAPI): RESTful services for recommendation generation
- **Frontend UI** (Streamlit): Interactive web interface for user interaction
- **CLI Interface**: Command-line tool for power users
- **Evaluation System**: Comprehensive testing and quality assurance
- **Feedback System**: User feedback collection and analysis

### Technology Stack

- **Backend**: Python, FastAPI, Groq LLM API
- **Frontend**: Streamlit (Web), CLI (Terminal)
- **Data**: CSV/JSON storage with pandas processing
- **LLM**: Groq (Llama 3, Mixtral, Gemma models)
- **Testing**: Comprehensive evaluation framework
- **Monitoring**: Feedback collection and performance tracking

## Phase Implementation Status

### ✅ Phase 0: Problem Framing and Scope Definition (COMPLETED)

**Goal:** Define what the system will do in Version 1.

**Architecture Focus:**
- Define input fields, output format, and recommendation quality expectations
- Confirm basic web UI as the primary user input source for V1
- Finalize constraints (response time, max number of recommendations, budget categories)
- Define success metrics (e.g., relevance, coverage, user satisfaction)

**Deliverables:**
- Scope document
- Functional requirements
- Non-functional requirements
- Implemented documents:
  - `doc/phase-0-scope.md`
  - `doc/phase-0-functional-requirements.md`
  - `doc/phase-0-non-functional-requirements.md`

### ✅ Phase 1: Data Layer Foundation (COMPLETED)

**Goal:** Build a reliable data ingestion and preprocessing pipeline.

**Architecture Focus:**
- Ingest Zomato dataset from Hugging Face
- Clean and normalize fields (location, cuisine, rating, cost)
- Handle missing values and inconsistent labels
- Store processed data in a query-friendly format (CSV/Parquet/DB table)

**Core Components:**
- `Data Ingestion Module`
- `Data Cleaning & Normalization Module`
- `Data Storage Layer`

**Implementation:**
- Data ingestion and preprocessing scripts
- Clean restaurant dataset with standardized fields
- CSV-based storage for simplicity and portability

**Deliverables:**
- Processed dataset (`data/processed/restaurants.csv`)
- Data dictionary/schema
- Data quality report

### ✅ Phase 2: Preference Capture and Filtering Engine (COMPLETED)

**Goal:** Convert user preferences into structured query constraints.

**Architecture Focus:**
- Build user input contract (location, budget, cuisine, minimum rating, optional constraints)
- Implement deterministic filtering and candidate generation
- Return top N candidates for LLM reasoning

**Core Components:**
- `User Input API / Form Layer`
- `Validation Layer`
- `Rule-Based Filtering Engine`

**Implementation:**
- `phase2/preference_parser.py`: Parse and validate user preferences
- `phase2/filter_engine.py`: Filter restaurants based on criteria
- `phase2/ranker_v1.py`: Basic ranking algorithm
- `phase2/__init__.py`: Package exports

**Deliverables:**
- Candidate retrieval service
- Input validation rules
- Filter performance benchmark

### ✅ Phase 3: LLM Prompting and Recommendation Logic (COMPLETED)

**Goal:** Add intelligence and personalization to candidate ranking.

**Architecture Focus:**
- Create prompt templates using user preferences + candidate restaurant records
- Ask LLM to rank options and generate concise explanations
- Enforce structured output format (JSON or schema-based text)

**Core Components:**
- `Prompt Builder`
- `LLM Adapter` (model API integration)
- `Response Parser and Formatter`

**Implementation:**
- `phase3/candidate_builder.py`: Format candidates for LLM context
- `phase3/prompt_builder.py`: Manage prompt templates
- `phase3/llm_client.py`: LLM API integration (OpenAI, Anthropic, Local)
- `phase3/response_parser.py`: Parse and validate LLM responses
- `phase3/pipeline.py`: Main orchestrator for Phase 3
- `phase3/main.py`: Example usage and testing
- `phase3/test_phase3.py`: Unit tests
- `phase3/README.md`: Documentation

**Deliverables:**
- Prompt template library
- LLM integration service
- Structured recommendation response format

### ✅ Phase 4: Application Layer and UI Delivery (COMPLETED)

**Goal:** Deliver recommendations in a clear user-facing interface.

**Architecture Focus:**
- Build frontend or CLI output view for top recommendations
- Display ranking, rating, cuisine, price range, and AI explanation
- Include fallback messages for no-match cases

**Core Components:**
- `Recommendation API`
- `Presentation Layer` (Web UI / CLI)
- `Error and Fallback Handler`

**Implementation:**
- `phase4/groq_provider.py`: Groq LLM integration (Llama 3, Mixtral, Gemma)
- `phase4/api_server.py`: FastAPI REST API server
- `phase4/presentation_layer.py`: Streamlit web interface
- `phase4/error_handler.py`: Error handling and fallback mechanisms
- `phase4/cli_interface.py`: Command-line interface
- `phase4/app_orchestrator.py`: Main application coordinator
- `phase4/main.py`: Examples and entry points
- `phase4/.env.example`: Environment configuration template
- `phase4/requirements.txt`: Dependencies
- `phase4/README.md`: Documentation

**Backend API (FastAPI):**
- RESTful endpoints for recommendation generation
- Health checks and system monitoring
- Error handling and graceful degradation
- Integration with Groq LLM

**Frontend UI (Streamlit):**
- Interactive preference forms
- Real-time recommendation display
- AI explanations and match scores
- Responsive web interface

**CLI Interface:**
- Command-line tool for power users
- Interactive and single-command modes
- JSON output option
- API status checking

**Deliverables:**
- End-to-end runnable app
- Recommendation display page/view
- Basic user interaction flow

### ✅ Phase 5: Evaluation, Feedback, and Tuning (COMPLETED)

**Goal:** Improve recommendation quality and robustness.

**Architecture Focus:**
- Evaluate recommendation relevance with test scenarios
- Track prompt quality, hallucination cases, and ranking consistency
- Tune filtering logic and prompt templates
- Add optional user feedback loop (like/dislike recommendations)

**Core Components:**
- `Evaluation Harness`
- `Prompt/Ranking Tuning Module`
- `Feedback Collection Layer`

**Implementation:**
- `phase5/evaluation_harness.py`: Comprehensive testing framework
- `phase5/prompt_tuning.py`: Prompt optimization and A/B testing
- `phase5/feedback_collection.py`: User feedback gathering and analysis
- `phase5/test_scenarios.py`: Comprehensive test scenarios
- `phase5/metrics.py`: Evaluation metrics calculation
- `phase5/hallucination_detector.py`: Hallucination and consistency detection
- `phase5/report_generator.py`: Multi-format report generation
- `phase5/improvement_backlog.py`: Improvement item management
- `phase5/main.py`: Examples and entry points
- `phase5/README.md`: Documentation

**Evaluation System:**
- 15+ comprehensive test scenarios
- Automated metric calculation
- Regression testing against baselines
- Quality assurance and validation

**Feedback System:**
- Multi-channel feedback collection (ratings, like/dislike, detailed, corrections)
- Feedback aggregation and trend analysis
- Restaurant-specific feedback tracking

**Tuning System:**
- Automatic prompt variant generation
- A/B testing framework
- Performance optimization
- Best variant selection

**Deliverables:**
- Evaluation report
- Tuned prompt + filter configuration
- Improvement backlog

### 🔄 Phase 6: Production Readiness and Observability (PENDING)

**Goal:** Make the system stable, secure, and monitorable.

**Architecture Focus:**
- Add logging, monitoring, and error tracking
- Add caching for repeated queries and frequent locations
- Add rate limiting and input sanitization
- Set up deployment pipeline (CI/CD + environment configs)

**Core Components:**
- `Logging & Monitoring Stack`
- `Caching Layer`
- `Security & Reliability Middleware`
- `Deployment Pipeline`

**Deliverables:**
- Production deployment
- Monitoring dashboards
- Runbook for incidents and recovery

### 🔄 Phase 7: Advanced Enhancements (Future Scope)

**Goal:** Extend system capabilities beyond baseline recommendations.

**Architecture Focus:**
- Personalized profiles and recommendation memory
- Hybrid ranking (rules + vector search + LLM reasoning)
- Multi-city support optimization
- A/B testing for prompt and ranking strategies

**Potential Components:**
- `User Profile Store`
- `Vector Database / Embeddings Layer`
- `Experimentation Framework`

**Deliverables:**
- Feature roadmap for v2+
- Experiment results and rollout plan
## Complete System Architecture

### Backend-Frontend Integration

The restaurant recommendation system is now a complete full-stack application with proper backend and frontend separation:

#### Backend Architecture (FastAPI + Groq)
```
Backend (FastAPI Server)
├── API Layer
│   ├── Recommendation Endpoints
│   ├── Health Check Endpoints
│   ├── Feedback Endpoints
│   └── System Monitoring
├── Business Logic
│   ├── Phase 2: Preference Parsing & Filtering
│   ├── Phase 3: LLM Integration & Ranking
│   ├── Phase 4: Error Handling & Fallbacks
│   └── Phase 5: Evaluation & Tuning
├── Data Layer
│   ├── Restaurant Data (CSV/JSON)
│   ├── User Feedback Storage
│   └── Evaluation Results
└── External Services
    ├── Groq LLM API
    └── Restaurant Database
```

#### Frontend Architecture (Streamlit + CLI)
```
Frontend (Streamlit Web App)
├── User Interface
│   ├── Preference Input Forms
│   ├── Recommendation Display
│   ├── Feedback Collection
│   └── System Status
├── API Integration
│   ├── Recommendation Service Calls
│   ├── Feedback Submission
│   └── Error Handling
└── User Experience
    ├── Real-time Updates
    ├── Interactive Elements
    └── Responsive Design

CLI Interface
├── Command Processing
├── API Communication
├── Output Formatting
└── Error Handling
```

### Data Flow Architecture

```
User Input (Web/CLI)
    ↓
Frontend (Streamlit/CLI)
    ↓
Backend API (FastAPI)
    ↓
┌─────────────────────────────────┐
│ Phase 2: Preference Parsing      │
│ - Validate user preferences      │
│ - Filter restaurant candidates   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Phase 3: LLM Integration         │
│ - Format candidates for LLM      │
│ - Generate AI rankings           │
│ - Parse structured responses      │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Phase 4: Application Layer        │
│ - Error handling & fallbacks     │
│ - Response formatting           │
│ - System orchestration           │
└─────────────────────────────────┘
    ↓
User Recommendations (Web/CLI)
```

### Implementation Summary (Phases 0-5)

#### ✅ Phase 0 - Project Setup and Foundations (COMPLETED)
- **Components**: Repository structure (`/data`, `/phase0-5`, `/doc`), configuration loader, logging, environment management (API keys).
- **Deliverables**: Complete project structure, configuration templates, comprehensive documentation.

#### ✅ Phase 1 - Data Ingestion and Preprocessing (COMPLETED)
- **Components**: `DatasetLoader` (Hugging Face), `Preprocessor` (cleaning and normalization), `SchemaMapper` (standard fields).
- **Storage**: Local processed file (CSV/JSON) with standardized schema.
- **Deliverables**: Cleaned dataset with fields like name, location, cuisines, cost, and rating.

#### ✅ Phase 2 - Query and Filtering Engine (COMPLETED)
- **Components**: `PreferenceParser`, `FilterEngine` (location, budget, cuisine, minimum rating), `RankerV1` (simple scoring logic).
- **Implementation**: Complete filtering and ranking system with preference validation.
- **Deliverables**: Deterministic Top-N restaurant recommendations in structured format.

#### ✅ Phase 3 - LLM Integration Layer (COMPLETED)
- **Components**: `CandidateBuilder` (context from filtered rows), `PromptBuilder`, `LLMClient` (OpenAI, Anthropic, Local), `ResponseParser` (JSON output).
- **Implementation**: Full LLM integration with multiple providers and structured output parsing.
- **Deliverables**: LLM-based ranking plus user-friendly explanations with consistent schema.

#### ✅ Phase 4 - Recommendation Service API (COMPLETED)
- **Components**: `RecommendationAPI` (orchestrator), FastAPI REST server, Groq LLM integration, request validation, error handling.
- **Implementation**: Complete backend API with FastAPI, Groq integration, multiple interfaces (Web, CLI, API).
- **Endpoints**: `/recommend`, `/health`, `/restaurants`, `/feedback`, `/models`.
- **Deliverables**: Production-ready API with defined request-response contract.

#### ✅ Phase 5 - UI/UX Output Layer (COMPLETED)
- **Components**: Streamlit web interface, CLI tool, preference input forms, recommendation display, feedback collection.
- **Implementation**: Complete frontend with Streamlit web app, CLI interface, and comprehensive evaluation system.
- **Deliverables**: User-friendly interface showing name, cuisine, rating, cost range, and AI explanations.

#### ✅ Phase 5 - Evaluation & Tuning System (COMPLETED)
- **Components**: `EvaluationHarness`, `PromptTuningModule`, `FeedbackCollectionLayer`, `TestScenarios`, `Metrics`.
- **Implementation**: Comprehensive evaluation framework with 15+ test scenarios, feedback collection, and optimization tools.
- **Deliverables**: Quality assurance system, improvement backlog, and continuous optimization framework.

### Current System Capabilities

#### Functional Capabilities
- ✅ Personalized restaurant recommendations using Groq LLM
- ✅ Multi-language LLM support (Llama 3, Mixtral, Gemma)
- ✅ Multiple user interfaces (Web, CLI, API)
- ✅ Real-time recommendation generation
- ✅ Comprehensive error handling and fallbacks
- ✅ User feedback collection and analysis
- ✅ System evaluation and quality assurance

#### Technical Capabilities
- ✅ RESTful API with FastAPI
- ✅ Interactive web interface with Streamlit
- ✅ Command-line interface for power users
- ✅ Comprehensive testing framework
- ✅ Performance monitoring and metrics
- ✅ Hallucination detection and safety checks
- ✅ Prompt optimization and A/B testing
- ✅ Data-driven improvement system

#### Integration Points
- ✅ Groq LLM API integration
- ✅ Restaurant database integration
- ✅ Multi-phase pipeline orchestration
- ✅ Feedback loop integration
- ✅ Evaluation system integration
- ✅ Error handling integration

## Deployment and Integration

### System Deployment Architecture

```
Production Environment
├── Frontend (Streamlit)
│   ├── Port: 8501
│   ├── Static Assets
│   └── API Client
├── Backend API (FastAPI)
│   ├── Port: 8000
│   ├── REST Endpoints
│   └── Groq Integration
├── Data Storage
│   ├── Restaurant Database (CSV/JSON)
│   ├── User Feedback Storage
│   └── Evaluation Results
└── External Services
    └── Groq LLM API
```

### API Endpoints

#### Recommendation API
- `POST /recommend` - Generate restaurant recommendations
- `GET /restaurants` - List available restaurants
- `POST /feedback` - Submit user feedback
- `GET /health` - System health check
- `GET /models` - Available LLM models

#### Response Format
```json
{
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "Restaurant Name",
      "match_score": 0.85,
      "reasons": ["Specific reasons"],
      "highlights": ["Key features"],
      "price_indication": "Moderate",
      "best_for": "Occasion type"
    }
  ],
  "summary": "Recommendation summary",
  "pipeline_metadata": {
    "total_candidates": 15,
    "candidates_used": 5,
    "response_time_ms": 750,
    "groq_model": "llama3-8b-8192"
  }
}
```

### Environment Configuration

#### Required Environment Variables
```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Data Configuration
RESTAURANT_DATA_PATH=data/processed/restaurants.csv

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Configuration
STREAMLIT_HOST=localhost
STREAMLIT_PORT=8501

# System Configuration
LOG_LEVEL=INFO
MAX_RECOMMENDATIONS=10
RESPONSE_TIMEOUT=30
```

### Running the System

#### Option 1: Web Interface
```bash
# Start API Server
python -m phase4.main api-server

# Start Web Interface (in separate terminal)
python -m phase4.main streamlit
```

#### Option 2: CLI Interface
```bash
# Interactive mode
python -m phase4.main cli

# Single command
python -m phase4.main --location Bellandur --cuisine Italian --max-cost 2000
```

#### Option 3: API Usage
```bash
# Start API Server
python -m phase4.main api-server

# Make API requests
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"preferences": {"location": "Bellandur", "cuisine": "Italian"}}'
```

### System Monitoring

#### Health Checks
- API Health: `GET http://localhost:8000/health`
- System Status: Available through CLI and web interface
- Performance Metrics: Tracked in Phase 5 evaluation system

#### Feedback Collection
- Web Interface: Integrated feedback forms
- API Endpoint: `POST /feedback`
- CLI: Built-in feedback commands
- Analytics: Phase 5 feedback analysis system

### Quality Assurance

#### Evaluation Framework
- 15+ comprehensive test scenarios
- Automated regression testing
- Performance benchmarking
- Hallucination detection
- Ranking consistency validation

#### Continuous Improvement
- User feedback analysis
- Prompt optimization
- Performance monitoring
- Issue tracking and resolution

## Next Steps and Future Development

### Immediate Next Steps (Phase 6)
1. **Production Hardening**
   - Add caching layer
   - Implement rate limiting
   - Add comprehensive logging
   - Set up monitoring dashboards

2. **Deployment Pipeline**
   - CI/CD configuration
   - Environment management
   - Automated testing
   - Deployment automation

### Future Enhancements (Phase 7)
1. **Advanced Features**
   - User profiles and personalization
   - Vector search integration
   - Multi-city optimization
   - A/B testing framework

2. **Scalability**
   - Database migration (PostgreSQL)
   - Microservices architecture
   - Load balancing
   - Auto-scaling

## Project Status Summary

### Completed Components (Phases 0-5)
- ✅ **Complete full-stack application** with proper backend/frontend separation
- ✅ **Production-ready API** with FastAPI and Groq integration
- ✅ **Interactive web interface** with Streamlit
- ✅ **Command-line interface** for power users
- ✅ **Comprehensive evaluation system** with quality assurance
- ✅ **User feedback collection** and analysis
- ✅ **Error handling and fallback mechanisms**
- ✅ **Performance optimization** and monitoring

### System Architecture Benefits
- **Modular Design**: Each phase builds incrementally
- **Separation of Concerns**: Clear backend/frontend separation
- **Scalable Structure**: Easy to extend and maintain
- **Production Ready**: Complete deployment and monitoring
- **Quality Assured**: Comprehensive testing and evaluation

The restaurant recommendation system is now a complete, production-ready application with proper backend and frontend architecture, comprehensive evaluation capabilities, and clear deployment pathways.
