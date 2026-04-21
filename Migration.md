# Migration Guide

This document helps developers move from the old repository at `Graph-Repair-using-LLMs-` to the structured layout in `dev-graph-repair-llm`.

## Why the layout changed

The old repo concentrated multiple responsibilities inside a few large files:

- workflow orchestration
- LLM client setup
- prompt strings
- graph repair node logic
- synthetic graph generation
- experiment evaluation
- snapshot helpers

The new layout separates those concerns so future work can scale without repeatedly editing the same files.

## Old to new file map

### Core repair workflow

- Old `main.py` -> New [main.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/main.py)
  This is now a thin entrypoint that builds and runs the workflow from package modules.

- Old `nodes.py` -> New [graph_repair/workflow/nodes.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/workflow/nodes.py)
  The repair logic is no longer mixed with ad hoc prompt strings or provider bootstrapping.

- Old `state.py` -> New [graph_repair/workflow/state.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/workflow/state.py)
  Workflow state is isolated so it can evolve independently.

- Old workflow assembly inside `main.py` -> New [graph_repair/workflow/app.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/workflow/app.py)
  Graph construction is now separate from the command-line entrypoint.

### LLM and prompts

- Old prompt text embedded in `nodes.py` and `prompt_template.py` -> New [graph_repair/prompts/repair.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/prompts/repair.py) and [graph_repair/prompts/query_generation.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/prompts/query_generation.py)
  Prompt content is now grouped by purpose.

- Old provider logic inside `nodes.py` -> New [graph_repair/llm/client.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/llm/client.py)
  Ollama and LM Studio setup now lives in one place.

### Database and schema

- Old `database.py` -> New [graph_repair/db.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/db.py)
  Neo4j access is centralized.

- Old `schema_extract.py` -> New [graph_repair/schema.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/schema.py) plus [scripts/show_schema.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/show_schema.py)
  APOC schema queries are separated from the CLI wrapper and the manual schema-inspection command now lives in `scripts/`.

### Synthetic graph generation and experiments

- Old `generator.py` -> New [graph_repair/synthetic/legacy_generator.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/synthetic/legacy_generator.py)
  The older synthetic graph and inconsistency injection logic has been preserved, but moved under a dedicated synthetic-data module.

- Old `evaluator.py` -> New [graph_repair/experiments/evaluator.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/evaluator.py)
  Experiment metrics are isolated from graph generation and workflow code.

- Old `snapshot_tool.py` -> New [graph_repair/experiments/snapshot.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/snapshot.py)
  Snapshot export and restore now live with the experiment utilities.

- Old `benchmark.py` -> New [scripts/benchmark.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/benchmark.py)
  This is now a runnable helper script that delegates into package code.

- Old `create_G.py` -> New [scripts/create_G.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/create_G.py)

- Old `create_G_in.py` -> New [scripts/create_G_in.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/create_G_in.py)

- Old `create_G_all_in.py` -> New [scripts/create_G_all_in.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/create_G_all_in.py)

- Old `dataset.py` -> New [scripts/load_pattern_dataset.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts/load_pattern_dataset.py)
  The file-based dataset loader is now a clearly named helper script.

- Old `patterns.txt` -> New [data/patterns.txt](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/data/patterns.txt)
  Static pattern data now lives in a dedicated data folder instead of the repository root.

## Functionality that is now split across multiple files

Several old single-file responsibilities are intentionally split:

### `nodes.py`

Old `nodes.py` mixed together:

- provider selection
- streaming LLM calls
- prompt construction
- schema handling
- workflow node logic

Now that functionality is split into:

- [graph_repair/workflow/nodes.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/workflow/nodes.py)
- [graph_repair/llm/client.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/llm/client.py)
- [graph_repair/prompts/repair.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/prompts/repair.py)
- [graph_repair/schema.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/schema.py)

### `main.py`

Old `main.py` mixed together:

- reading inconsistencies
- workflow construction
- workflow execution
- experiment startup in the older repo

Now that is split into:

- [main.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/main.py) for the app entrypoint
- [graph_repair/workflow/app.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/workflow/app.py) for workflow assembly
- [graph_repair/experiments/runner.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/runner.py) for the synthetic experiment flow

### Legacy experiment flow

Old experiment-related behavior was spread across standalone files with direct cross-imports.

Now it is split by concern:

- synthetic generation in [graph_repair/synthetic/legacy_generator.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/synthetic/legacy_generator.py)
- evaluation in [graph_repair/experiments/evaluator.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/evaluator.py)
- snapshot handling in [graph_repair/experiments/snapshot.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/snapshot.py)
- orchestration in [graph_repair/experiments/runner.py](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/graph_repair/experiments/runner.py)
- runnable helpers in [scripts](/Users/narendradevireddy/Desktop/development/dev-graph-repair-llm/scripts)

## What was intentionally removed from the root

These old-style compatibility wrappers are no longer needed in the repository root:

- `nodes.py`
- `database.py`
- `state.py`
- `prompt_template.py`
- `dataset.py`
- `schema_extract.py`
- `generator.py`
- `evaluator.py`
- `snapshot_tool.py`
- `benchmark.py`
- `create_G.py`
- `create_G_in.py`
- `create_G_all_in.py`

Their behavior now lives either inside `graph_repair/` or `scripts/`.

## Recommended developer workflow

- Work on repair behavior in `graph_repair/workflow/`
- Work on prompt quality in `graph_repair/prompts/`
- Work on provider integration in `graph_repair/llm/`
- Work on Neo4j helpers in `graph_repair/db.py` and `graph_repair/schema.py`
- Work on synthetic graph and experiment evaluation in `graph_repair/synthetic/` and `graph_repair/experiments/`
- Use `scripts/` only for runnable helper entrypoints
- Keep sample inputs and static data in `data/`
