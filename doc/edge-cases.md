## Detailed Edge Cases (Phase-Wise)

This document provides detailed, phase-wise edge cases for the restaurant recommendation system.
References:
- `doc/problem statement.md`
- `doc/phase-wise architecture.md`

---

## Phase 0: Problem Framing and Scope Definition

### Edge Cases
- Success metrics are not measurable (e.g., "good recommendations" without KPI).
- Business goals conflict (high personalization vs low latency vs low LLM cost).
- Scope is too broad in V1 (real-time personalization, multilingual, A/B testing together).
- No fallback behavior defined when LLM fails or no matches are found.
- Unclear Top-N rule (fixed N vs dynamic N) causes inconsistent UX.

### Impact
- Hard to validate if the project is successful.
- Team members implement different assumptions.
- Rework in later phases due to unclear requirements.

### Recommended Handling
- Define measurable KPIs: precision@N, response latency, coverage, satisfaction score.
- Freeze V1 scope and mark future features as Phase 7.
- Document mandatory fallback behavior and output schema early.

---

## Phase 1: Data Ingestion and Preprocessing

### Edge Cases
- Hugging Face dataset is temporarily unavailable or rate-limited.
- Schema drift: column names change (`city` -> `location`, `avg_cost` missing).
- Missing mandatory values: cuisine, cost, rating, location.
- Inconsistent formats:
  - rating as `4.3`, `4.3/5`, `NEW`, `-`
  - cost as `500`, `Rs. 500`, `500 for two`
- Duplicate records for same restaurant with minor text differences.
- City alias issues (`Bangalore`, `Bengaluru`, `BLR`).
- Unicode or encoding corruption in names/cuisines.
- Very large raw dataset causes memory spikes during cleaning.

### Impact
- Bad candidate quality and unstable rankings.
- Filter engine misses valid restaurants.
- Pipeline crashes or takes too long.

### Recommended Handling
- Add schema validation and fail-fast checks.
- Use normalization maps for city and cuisine aliases.
- Standardize rating/cost into numeric canonical fields.
- Add deduplication logic (`name + city + address` heuristic).
- Use chunked processing for large files.

---

## Phase 2: Preference Capture and Filtering Engine

### Edge Cases
- Empty request (no user preferences at all).
- Invalid input types (rating as text, budget as number, malformed JSON).
- Out-of-range values (rating < 0 or > 5).
- Unsupported budget label (`cheap`, `premium`) not mapped to categories.
- Contradictory constraints:
  - low budget + very high rating + niche cuisine
  - family-friendly + late-night only in low-density areas
- Ambiguous cuisine matching (`Indian` vs `North Indian`, `Chinese` vs `Pan-Asian`).
- Multi-cuisine parsing errors (`Italian, Continental` treated as one token).
- Over-filtering leads to zero candidates.
- Under-filtering leads to too many candidates and high latency.
- Tie scores in baseline ranking produce unstable order.

### Impact
- No recommendations or irrelevant recommendations.
- Inconsistent results for same input.
- Increased LLM cost due to oversized candidate set.

### Recommended Handling
- Strict request validation with clear error messages.
- Soft relaxation strategy for zero-result cases (relax one constraint at a time).
- Cap candidate set before LLM (e.g., Top 30 deterministic shortlist).
- Stable tie-breakers (`rating desc`, `cost fit score`, `name asc`).

---

## Phase 3: LLM Prompting and Recommendation Logic

### Edge Cases
- Prompt token overflow when candidate list is too large.
- LLM returns unstructured text instead of required JSON/schema.
- Hallucinated restaurants not present in candidate input.
- LLM ignores hard constraints (city/budget/minimum rating).
- LLM repeats same candidate multiple times.
- Response language mismatch with user language.
- Unsafe wording, bias, or policy-violating output.
- Timeout or transient provider/network failure.
- Model version change causes output format drift.

### Impact
- Parsing failures and broken response pipeline.
- Trust loss due to fabricated recommendations.
- Non-compliant or low-quality user-facing output.

### Recommended Handling
- Enforce strict response schema with parser validation.
- Reject outputs containing unknown restaurant IDs/names.
- Use constrained prompts with explicit hard-rule checks.
- Add LLM retries with bounded backoff and timeout limits.
- Fallback to deterministic Phase 2 ranking when LLM fails.

---

## Phase 4: Application Layer, API, and UI Delivery

### Edge Cases
- Missing required API fields in request payload.
- Response schema mismatch between backend and frontend.
- UI shows rank order different from backend rank.
- Duplicate cards shown due to client-side merge bug.
- Very long explanations break card layout.
- Empty-state not handled (blank screen for zero candidates).
- CLI and web output differ in truncation/format rules.
- Partial response returned without clear degradation message.

### Impact
- Broken user experience despite correct core logic.
- Support burden due to confusing behavior.
- Lower user trust in recommendation quality.

### Recommended Handling
- Contract tests for request/response schema.
- Unified rendering rules and character limits per field.
- Explicit states: loading, success, no results, degraded mode, error.
- Include `source`/`mode` field in response (`llm`, `fallback_ranker`).

---

## Phase 5: Evaluation, Feedback, and Tuning

### Edge Cases
- Evaluation dataset is too narrow (few cities/cuisines only).
- Offline metrics improve but real user satisfaction drops.
- Feedback skew: only unhappy users submit ratings.
- Prompt improvements increase fluency but reduce factual correctness.
- No regression checks after changing filter logic.
- Human evaluation criteria are inconsistent across reviewers.

### Impact
- False confidence in model quality.
- Incorrect optimization decisions.
- Hidden quality regressions after updates.

### Recommended Handling
- Maintain representative benchmark sets by city, cuisine, and budget.
- Track both ranking quality and explanation quality separately.
- Add regression suite for deterministic and LLM outputs.
- Use weighted feedback and minimum sample thresholds before tuning.

---

## Phase 6: Production Readiness and Observability

### Edge Cases
- Cache serves stale recommendations after data refresh.
- No correlation ID across request -> filter -> LLM -> response.
- Retry storm during LLM outage increases latency and cost.
- Rate limiting missing or too lenient under traffic spikes.
- Logs leak secrets (API keys) or sensitive prompt fragments.
- Monitoring exists but lacks useful alerts by failure type.
- Fallback triggers silently, making quality drops hard to diagnose.

### Impact
- Reliability incidents and higher operational cost.
- Security and compliance risks.
- Slow incident response and root-cause analysis.

### Recommended Handling
- Cache invalidation tied to dataset/version hash.
- End-to-end request tracing with correlation IDs.
- Circuit breaker + capped retries + timeout budgets.
- Redact secrets and sensitive fields from logs.
- Alert on fallback rate, hallucination rejections, timeout ratio.

---

## Phase 7: Advanced Enhancements (Future Scope)

### Edge Cases
- Cold-start users have no profile for personalization.
- Personalization drift overfits old preferences and ignores recent intent.
- Vector retrieval returns semantically similar but constraint-violating items.
- Hybrid ranker conflicts (rule score vs vector score vs LLM score).
- A/B testing contamination due to inconsistent user bucketing.
- Multi-city expansion introduces city-level bias in ranking.

### Impact
- Personalization feels inaccurate or unfair.
- Complex ranking becomes unstable and hard to explain.
- Experiments produce unreliable conclusions.

### Recommended Handling
- Use fallback generic profile for cold-start users.
- Time-decay preference weights to prioritize recent behavior.
- Apply hard constraints after vector retrieval (post-filter).
- Define score blending policy and monitor per-component contribution.
- Use sticky bucketing for A/B cohorts.

---

## Cross-Phase Critical Fallback Rules

- If no candidates after filtering: relax one constraint at a time and explain the relaxation.
- If LLM fails or output is invalid: return deterministic Phase 2 Top-N with a safe message.
- If candidate has missing key fields: either exclude it or label as `Not available`.
- If latency exceeds SLA: return partial/fallback results with traceable status.
- If security checks fail: reject request with sanitized error response.
