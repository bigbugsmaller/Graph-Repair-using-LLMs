# LangGraph Neo4j Agent

This project implements a LangGraph-based agent that interacts with a Neo4j graph database. It supports local LLM providers and now includes a structured package layout for the repair workflow, prompts, and experiment tooling that was previously scattered across standalone scripts.

## Prerequisites

- Python 3.8+
- Neo4j Database (AuraDB or Local)
- LLM Provider (choose one):
  - **Ollama** (default) - Local LLM server
  - **LM Studio** - OpenAI-compatible local LLM server

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
   - `LLM_PROVIDER` - Set to `ollama` (default) or `lm-studio`
   - For Ollama: `OLLAMA_HOST`, `OLLAMA_MODEL` (defaults: `http://localhost:11434`, `llama3.1`)
   - For LM Studio: `LM_STUDIO_HOST`, `LM_STUDIO_MODEL` (defaults: `http://localhost:1234`, `meta-llama-3.1-8b-instruct`)

See `LLM_PROVIDER_GUIDE.md` for detailed configuration options.

## Project Structure

Core code now lives under `graph_repair/`:

```text
graph_repair/
  db.py                    # Neo4j wrapper
  schema.py                # APOC-based schema extraction helpers
  llm/
    client.py              # Ollama / LM Studio client selection and streaming
  prompts/
    query_generation.py    # Prompt template for Cypher generation
    repair.py              # Prompt builders for inconsistency description/repair
  workflow/
    state.py               # LangGraph agent state
    nodes.py               # Repair workflow nodes
    app.py                 # Workflow builder
  synthetic/
    legacy_generator.py    # Synthetic graph + violation generator from old repo
  experiments/
    evaluator.py           # GED / validity / fidelity evaluation
    snapshot.py            # Snapshot export/restore helpers
    runner.py              # End-to-end experiment orchestration
```

The repository root is kept lighter now. Reusable application code belongs in `graph_repair/`, while runnable helper commands belong in `scripts/`.

## Run

```bash
python main.py
```

`main.py` reads `inconsistency.txt` or `inconsistencies.txt` and iteratively:
- queries Neo4j for each inconsistency pattern
- extracts the live graph schema
- asks the LLM to generate a repair Cypher statement
- applies the repair and re-checks until the inconsistency no longer matches

## Utilities

### Graph Generation (`graph_generator.py`)

Generate fictitious graphs for testing and development with two modes:

**Parametric Mode** - Generate abstract graphs with N nodes and E edges:
```bash
# Generate 100 nodes and 500 edges
python graph_generator.py --nodes 100 --edges 500

# Custom prefixes
python graph_generator.py --nodes 50 --edges 200 --node-prefix Person --edge-prefix Knows
```

**Schema-Driven Mode** - Generate domain-specific graphs from YAML configs:
```bash
# Academic domain (students, courses, professors)
python graph_generator.py --config examples/academic_graph.yaml

# Healthcare domain (patients, doctors, medications)
python graph_generator.py --config examples/health_graph.yaml

# Custom domain
python graph_generator.py --config examples/custom_domain.yaml
```

**Features:**
- Random graph generation (Erdős–Rényi algorithm)
- Faker integration for realistic data
- Built-in Academic and Health domain ontologies
- Support for weighted/unweighted edges
- Uni/bidirectional relationships
- Custom properties on nodes and edges
- Interactive database wipe prompt (or use `--wipe`/`--no-wipe`)

**Programmatic Usage:**
```python
from graph_generator import GraphGenerator
import config

gen = GraphGenerator(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)

# Parametric mode
gen.generate_parametric(num_nodes=100, num_edges=500, wipe_db=True)

# Schema-driven mode
gen.generate_from_config('examples/academic_graph.yaml', wipe_db=True)

gen.close()
```

### Other Utilities

- Generate (destructive) pattern-based synthetic data:
  - `scripts/load_pattern_dataset.py` wipes the database (`MATCH (n) DETACH DELETE n`) before loading patterns from `data/patterns.txt`.
- Inspect the current graph schema:
  - `scripts/show_schema.py`
- Run the synthetic end-to-end experiment flow:
  - `scripts/benchmark.py`
- Export graph snapshots:
  - `scripts/snapshot_tool.py`
- Create synthetic clean / inconsistent graphs used by the experiment flow:
  - `scripts/create_G.py`
  - `scripts/create_G_in.py`
  - `scripts/create_G_all_in.py`
