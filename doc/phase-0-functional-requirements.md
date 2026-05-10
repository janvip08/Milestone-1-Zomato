## Phase 0 Functional Requirements (V1)

## 1) User Input and Validation

### FR-0: Input Source (Basic Web UI)
The system shall use a basic web UI as the primary input channel for collecting user preferences in V1.

### FR-1: Capture Preferences
The system shall accept user preferences for:
- location
- budget (`low`, `medium`, `high`)
- cuisine
- minimum rating
- optional additional constraints

### FR-2: Validate Input
The system shall validate:
- required fields are present (at least location + one preference dimension)
- budget is in allowed values
- minimum rating is within accepted range
- text inputs are sanitized

### FR-3: Input Error Feedback
The system shall return clear validation errors for invalid or incomplete requests.

### FR-3a: UI Input Form Behavior
The basic web UI shall provide a form with fields for location, budget, cuisine, minimum rating, and optional constraints, and display validation messages inline.

## 2) Data Handling

### FR-4: Dataset Ingestion
The system shall load restaurant data from the configured dataset source.

### FR-5: Data Normalization
The system shall normalize fields required for ranking:
- location/city
- cuisine tags
- rating
- cost/price

### FR-6: Candidate Dataset Preparation
The system shall provide a cleaned and query-ready dataset for filtering.

## 3) Recommendation Pipeline

### FR-7: Deterministic Candidate Filtering
The system shall filter restaurants based on user preferences and generate a shortlist.

### FR-8: Candidate Limit
The system shall cap candidates before LLM invocation to control token usage and latency.

### FR-9: LLM Ranking
The system shall send shortlisted candidates + user preferences to the LLM for ranking.

### FR-10: Explanation Generation
The system shall generate concise recommendation explanations for each selected restaurant.

### FR-11: Structured Output
The system shall return recommendations in a consistent schema containing:
- restaurant name
- cuisine
- rating
- estimated cost/price range
- explanation

## 4) Fallback and Error Handling

### FR-12: No-Match Handling
If no candidates match strict filters, the system shall apply controlled relaxation (one rule at a time) or return an explicit no-result message.

### FR-13: LLM Failure Fallback
If LLM call fails or output is invalid, the system shall return deterministic ranking output from the baseline ranker.

### FR-14: Safe Output Guardrails
The system shall reject LLM recommendations that are not present in the candidate list.

## 5) Phase-0 Completion Requirements

### FR-15: Documentation Completeness
The system documentation shall include:
- scope
- functional requirements
- non-functional requirements
- edge cases
- phase-wise architecture

### FR-16: Traceability
Each functional requirement shall map to implementation tasks in later phases.
