## Phase 0 Scope Document

Project: AI-Powered Restaurant Recommendation System (Zomato Use Case)

## 1) Purpose

Define the Version 1 (V1) scope, boundaries, and success criteria before implementation starts.

## 2) Problem Statement

Users need quick and relevant restaurant recommendations based on preferences such as location, budget, cuisine, and minimum rating. A hybrid approach (structured filtering + LLM reasoning) is used to produce ranked recommendations with concise explanations.

## 3) In-Scope (V1)

- Ingest and preprocess the Zomato dataset from the specified Hugging Face source.
- Provide a basic web UI as the primary source of user input.
- Accept user preferences:
  - location
  - budget (`low`, `medium`, `high`)
  - cuisine
  - minimum rating
  - optional additional constraints (text)
- Apply deterministic filtering to generate candidate restaurants.
- Use an LLM to rank candidates and produce short explanations.
- Return top recommendations in a consistent output format:
  - restaurant name
  - cuisine
  - rating
  - estimated cost/price range
  - AI explanation
- Provide fallback behavior when no result or LLM failure occurs.

## 4) Out-of-Scope (V1)

- Real-time menu/pricing updates from live restaurant APIs.
- User accounts, authentication, and long-term personalization memory.
- Payments, table booking, or delivery integration.
- Multi-lingual conversational interface (beyond basic text input).
- A/B testing framework and advanced experimentation tooling.
- Full production-grade autoscaling infrastructure.

## 5) Key Assumptions

- Dataset has enough coverage and quality for major city-level recommendations.
- LLM API access is available and stable for inference.
- Initial usage is moderate and suitable for single-service architecture.
- Recommendations are advisory; final user decision is outside system control.

## 6) Constraints

- Response latency target should remain practical for interactive usage.
- LLM usage must be cost-aware (candidate limit before prompt).
- Output must follow a stable schema for UI/API consumption.
- System should degrade gracefully if LLM or dataset service is unavailable.

## 7) Risks and Mitigation (Phase 0 View)

- **Schema drift in dataset** -> enforce schema validation before processing.
- **LLM hallucination** -> restrict recommendations to pre-filtered candidates only.
- **No-match scenarios** -> controlled filter relaxation and user-friendly messaging.
- **Latency spikes** -> candidate cap, timeout handling, and deterministic fallback.

## 8) Success Criteria (V1 Exit Criteria)

- System returns recommendations for common valid inputs with consistent schema.
- For no-match cases, user receives explicit fallback response (not blank/error).
- LLM output is validated and contains no out-of-candidate hallucinated items.
- Basic evaluation report is produced for relevance and response quality.

## 9) Deliverables

- `doc/phase-0-scope.md` (this document)
- `doc/phase-0-functional-requirements.md`
- `doc/phase-0-non-functional-requirements.md`
- Basic web UI wireframe/input flow definition (captured in requirements for implementation in next phase)
