## Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation service inspired by Zomato. The system should generate intelligent, personalized restaurant suggestions by combining a real-world restaurant dataset (structured data) with a Large Language Model (LLM) to produce human-like recommendations and explanations.

## Objective

Design and implement an application that:

- Accepts user preferences (e.g., location, budget, cuisine, rating threshold)
- Uses a real-world dataset of restaurants
- Leverages an LLM to rank options and generate personalized recommendations
- Presents results in a clear, user-friendly format

## System Workflow

### 1) Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face: `https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation`
- Extract relevant fields (as available in the dataset), such as:
  - Restaurant name
  - Location/city
  - Cuisine(s)
  - Cost/price range
  - Rating
  - Any other useful metadata

### 2) User Input

Collect user preferences, such as:

- Location (e.g., Delhi, Bangalore)
- Budget (low / medium / high)
- Cuisine (e.g., Italian, Chinese)
- Minimum rating
- Additional constraints (e.g., family-friendly, quick service)

### 3) Integration Layer (Data + LLM)

- Filter and prepare a relevant subset of restaurants based on user inputs.
- Construct an LLM prompt that includes the structured restaurant options and the user’s preferences.
- Ensure the prompt encourages the LLM to compare, reason, and rank options (not just list them).

### 4) Recommendation Engine

Use the LLM to:

- Rank the candidate restaurants
- Provide a short, user-facing explanation for each recommendation (why it fits the preferences)
- Optionally summarize trade-offs or highlight the “best match” based on the inputs

### 5) Output Display

Present the top recommendations in a user-friendly format, including:

- Restaurant name
- Cuisine
- Rating
- Estimated cost / price range
- AI-generated explanation

> Note: The detailed phase-wise architecture is available in `doc/phase-wise architecture.md`.
> Note: The project edge cases are documented in `doc/edge-cases.md`.