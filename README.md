# LangGraph Neo4j Agent

This project implements a LangGraph-based agent that interacts with a Neo4j graph database. It uses Ollama for LLM capabilities to generate Cypher queries and repair database inconsistencies.

## Prerequisites

- Python 3.8+
- Neo4j Database (AuraDB or Local)
- Ollama running locally (default) or a compatible remote endpoint

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

This repo reads configuration from environment variables (optionally loaded from a local `.env` file).

1. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
2. Fill in at least:
   - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
   - `OLLAMA_HOST`, `OLLAMA_MODEL` (defaults assume local Ollama at `http://localhost:11434`)

## Run

```bash
python main.py
```

`main.py` reads `inconsistency.txt` and iteratively:
- queries Neo4j for each inconsistency pattern
- asks the LLM to generate a repair Cypher statement
- applies the repair and re-checks until the inconsistency no longer matches

## Utilities

- Generate (destructive) synthetic data:
  - `dataset.py` wipes the database (`MATCH (n) DETACH DELETE n`) before loading patterns.
- Extract schema via APOC meta (requires APOC installed/enabled in Neo4j):
  - `schema_extract.py`
