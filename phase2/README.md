## Phase 2: Query and Filtering Engine (Non-LLM Baseline)

Implements Phase 2 from `doc/phase-wise architecture.md`.

### Components
- `preference_parser.py` -> `PreferenceParser` and `UserPreferences`
- `filter_engine.py` -> deterministic filtering by location, budget, cuisine, rating
- `ranker_v1.py` -> simple deterministic scoring and Top-N ranking
- `pipeline.py` -> end-to-end orchestration
- `main.py` -> CLI entry point

### Example run

`python -m phase2.main --dataset phase1/output/processed_dataset.csv --location bangalore --budget medium --cuisine "north indian" --min-rating 3.5 --top-n 5`

### Input
- Processed CSV from Phase 1 (default: `phase1/output/processed_dataset.csv`)
- User preferences from CLI payload

### Output
- Top-N structured recommendations with baseline `score`

