## Phase 1: Data Ingestion and Preprocessing

This folder implements Phase 1 from `doc/phase-wise architecture.md`.

### Components
- `dataset_loader.py`: Loads dataset from local JSON/CSV or Hugging Face.
- `schema_mapper.py`: Maps varied source columns to canonical schema.
- `preprocessor.py`: Cleans and normalizes location, cuisine, cost, and rating.
- `pipeline.py`: Orchestrates ingestion -> mapping -> preprocessing -> storage.
- `main.py`: Simple CLI runner for local processing.

### Sample Run

Use Python from project root:

`python -m phase1.main --input-file phase1/data/sample_restaurants.json --output-dir phase1/output`

### Output Deliverables

After running pipeline, `phase1/output` will contain:
- `processed_dataset.json`
- `processed_dataset.csv`
- `data_dictionary.md`
- `data_quality_report.json`

