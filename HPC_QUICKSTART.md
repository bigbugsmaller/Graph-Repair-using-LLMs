# HPC Quickstart

This guide explains how to test and run `dev-graph-repair-llm` on Sharanga HPC using a local Ollama server inside a Slurm job.

It is intentionally project-specific. For general cluster usage, storage rules, GPU booking, and Ollama container details, use the separate HPC runbooks your team already maintains.

## What This Project Needs

Before you try to run the project on HPC, make sure you have:

- a clone of this repository under your HPC home directory
- a Python environment installed under Scratch
- a reachable Neo4j database
- a small Ollama model available on the cluster
- a writable log/output directory under Scratch

This project does **not** need Neo4j to run on the same HPC node. In practice:

- Ollama runs inside your Slurm job on the allocated GPU node
- Neo4j is usually external
  - Neo4j Aura
  - a lab server
  - a local machine reachable from HPC

## Recommended Directory Layout

```bash
/home/hrishikesh/users/$USER_ALIAS/dev-graph-repair-llm
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair
/scratch/hrishikesh/users/$USER_ALIAS/logs/dev-graph-repair-llm
/scratch/hrishikesh/users/$USER_ALIAS/results/dev-graph-repair-llm
/scratch/hrishikesh/users/$USER_ALIAS/tmp
```

## Required Environment Variables

Create the project `.env` file or export these in the job script.

### Neo4j

```env
NEO4J_URI=<your_neo4j_uri>
NEO4J_USERNAME=<your_username>
NEO4J_PASSWORD=<your_password>
NEO4J_DATABASE=<your_database>
```

### LLM

For HPC, use Ollama:

```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Start with a small model first:

- `tinyllama`
- `smollm:135m`
- `llama3.2:1b`
- `llama3.2:3b`

## Python Environment

Recommended environment location:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair
```

Install dependencies using the full Python path from that environment:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/pip install -r requirements.txt
```

## Safe First Test Sequence

Do not start with a long benchmark run. Validate infrastructure in small steps.

### 1. Check Neo4j connectivity

```bash
cd /home/hrishikesh/users/$USER_ALIAS/dev-graph-repair-llm
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/show_schema.py
```

This confirms:

- the compute node can reach Neo4j
- the credentials are correct
- the database exists

### 2. Check Ollama connectivity

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python test_llm_providers.py
```

This confirms:

- Ollama is reachable at `http://localhost:11434`
- the selected model can answer a simple prompt

### 3. Create small test data

Use one of these paths:

Pattern-based loader:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/load_pattern_dataset.py
```

Synthetic graph generation:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/create_G.py
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/create_G_in.py
```

### 4. Run the repair loop

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python main.py
```

### 5. Only after that, run the full experiment

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/benchmark.py
```

## Recommended Slurm Pattern

The project expects Ollama to be available locally at `localhost:11434`, so the usual HPC pattern is:

1. request a GPU job
2. start `ollama serve` inside the job
3. wait for the server to be ready
4. run project commands in the same job
5. save logs and artifacts to Scratch

## Logging Recommendations

At minimum, keep three kinds of logs.

### 1. Slurm log

Use a dedicated output path:

```bash
#SBATCH --output=/scratch/hrishikesh/users/<firstname_rollno>/logs/dev-graph-repair-llm/slurm-%j.log
```

### 2. Per-run metadata

Capture job metadata in a small text file:

```bash
export PROJECT_ROOT=/home/hrishikesh/users/$USER_ALIAS/dev-graph-repair-llm
export PROJECT_LOG_DIR=/scratch/hrishikesh/users/$USER_ALIAS/logs/dev-graph-repair-llm
export PROJECT_OUT_DIR=/scratch/hrishikesh/users/$USER_ALIAS/results/dev-graph-repair-llm

mkdir -p "$PROJECT_LOG_DIR" "$PROJECT_OUT_DIR"

echo "job_id=$SLURM_JOB_ID" >  $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
echo "node=$SLURMD_NODENAME" >> $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
echo "model=$OLLAMA_MODEL" >> $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
echo "project_root=$PROJECT_ROOT" >> $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
date >> $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
git -C "$PROJECT_ROOT" rev-parse HEAD >> $PROJECT_LOG_DIR/run_${SLURM_JOB_ID}.meta
```

### 3. Application transcript

Wrap the Python command in `tee`:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python main.py \
  2>&1 | tee "$PROJECT_LOG_DIR/main_${SLURM_JOB_ID}.log"
```

For benchmarks:

```bash
/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python scripts/benchmark.py \
  2>&1 | tee "$PROJECT_LOG_DIR/benchmark_${SLURM_JOB_ID}.log"
```

## Saving Artifacts

If a run generates snapshots or ontology files, copy them to a stable results directory:

```bash
cp "$PROJECT_ROOT"/snapshot_* "$PROJECT_OUT_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/ontology_final.json "$PROJECT_OUT_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/inconsistency.txt "$PROJECT_OUT_DIR"/inconsistency_${SLURM_JOB_ID}.txt 2>/dev/null || true
cp "$PROJECT_ROOT"/inconsistencies.txt "$PROJECT_OUT_DIR"/inconsistencies_${SLURM_JOB_ID}.txt 2>/dev/null || true
```

## Sample Job Skeleton

This is a minimal pattern, not a full production script:

```bash
#!/bin/bash
#SBATCH --job-name=graph_repair_<firstname_rollno>
#SBATCH --partition=gpu_a100_8
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/scratch/hrishikesh/users/<firstname_rollno>/logs/dev-graph-repair-llm/slurm-%j.log

export USER_ALIAS=<firstname_rollno>
export PROJECT_ROOT=/home/hrishikesh/users/$USER_ALIAS/dev-graph-repair-llm
export PROJECT_LOG_DIR=/scratch/hrishikesh/users/$USER_ALIAS/logs/dev-graph-repair-llm
export PROJECT_OUT_DIR=/scratch/hrishikesh/users/$USER_ALIAS/results/dev-graph-repair-llm
export TMPDIR=/scratch/hrishikesh/users/$USER_ALIAS/tmp
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b

mkdir -p "$PROJECT_LOG_DIR" "$PROJECT_OUT_DIR" "$TMPDIR"

cd "$PROJECT_ROOT"

# Start Ollama here using your lab's standard container pattern.
# Then wait until curl http://localhost:11434/ succeeds.

/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python test_llm_providers.py \
  2>&1 | tee "$PROJECT_LOG_DIR/provider_${SLURM_JOB_ID}.log"

/scratch/hrishikesh/users/$USER_ALIAS/conda_envs/env_graph_repair/bin/python main.py \
  2>&1 | tee "$PROJECT_LOG_DIR/main_${SLURM_JOB_ID}.log"
```

## Common Failure Modes

### `Cannot connect to Ollama`

Likely causes:

- the Ollama server was never started inside the Slurm job
- `OLLAMA_HOST` is wrong
- the selected model is not available

### `Neo4j authentication/network error`

Likely causes:

- bad credentials
- wrong database name
- the compute node cannot reach your Neo4j endpoint

### `No such patterns in the knowledge graph`

Likely causes:

- the dataset was never generated
- the inconsistency queries do not match the current graph

### `Procedure not found: apoc.*`

Likely causes:

- your Neo4j instance does not have APOC installed
- the project path you are using expects APOC and does not yet have a fallback

## Recommended First Real HPC Test

Use this exact progression:

1. small Ollama model
2. `scripts/show_schema.py`
3. `test_llm_providers.py`
4. `scripts/create_G.py`
5. `scripts/create_G_in.py`
6. `main.py`

This sequence is the fastest way to separate:

- cluster setup issues
- Neo4j connectivity issues
- Ollama issues
- project logic issues

from each other.
