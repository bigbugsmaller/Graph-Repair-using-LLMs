# Checklist

## How to Use This File

- Treat it as the **stable checklist** of requirements
- Track active tasks and completed work in `TODO.md`

## Setup
- Create `.env` from `.env.example` with valid Neo4j and Ollama credentials.
- Verify connectivity: run `python schema_extract.py` and confirm it prints a schema.
- Confirm `python main.py` runs end-to-end (even with a tiny dummy inconsistency list).

## Define Constraints (Cypher-first)
Create `constraints.py` with **one Cypher query per constraint** (returns violating patterns).
Example constraints:
- **Type consistency** (A must connect only to B):
  - `MATCH (a:TypeA)-[:TO]->(c:TypeC) RETURN a,c;`
- **No mutual TO edges**:
  - `MATCH (a)-[:TO]->(b)-[:TO]->(a) RETURN a,b;`
- **Property range** (if using scores):
  - `MATCH (n) WHERE n.score < 0 OR n.score > 1 RETURN n;`

Output format (per constraint):
```
Constraint(id="type_consistency", query="MATCH ...")
```

## 1. Verifier (Deterministic)
Create `verifier.py`:
- For each constraint, run the Cypher query.
- Return `violations_count` and example nodes/edges (limit 5).
- **Goal:** no LLM here, only deterministic checks.

## 2. Generator + Noise (Reproducible)
Create `generator.py`:
- Start from a clean graph G that satisfies all constraints
- Inject noise to make G_in:
  - delete edges (missing edges)
  - add edges (spurious edges)
  - flip labels (label noise)
  - mutate properties (value noise)
- Use a fixed `seed` for RNG and log it

## 3. Repair Loop (LLM)
Create `runner.py`:
- For each constraint violation, ask the LLM for **one minimal Cypher repair**.
- Apply repair, then re-verify.
- Stop when violations are 0 or `max_iters` reached.

Prompt requirements:
- Include **schema** from `schema_extract.py`.
- Include the **exact violating pattern** returned by the verifier.
- Require output to be **only Cypher**, ending with `;`.

## Logging (Required)
Write one JSON line per iteration:
```
{
  "constraint_id": "...",
  "violations_before": 3,
  "proposed_cypher": "MATCH ... DELETE ...;",
  "applied": true,
  "violations_after": 1,
  "edit_cost": 1,
  "seed": 1234
}
```

## Metrics

- **Constraint satisfaction:** remaining violations per constraint
- **Minimality:** edit cost (#edges deleted/added + #labels changed + #properties changed)
- **Stability:** iterations to reach 0 violations
- **False positives:** count of repairs to constraints that were intentionally fake

## Baselines

- **Greedy repair:** apply the first valid repair (no LLM)
- **Random repair:** random delete/add within the violating subgraph
- **LLM-only:** with/without verifier feedback

## File Layout
```
constraints.py
generator.py
verifier.py
runner.py
metrics.py
logs/
```

## Deliverables
- 3 constraints implemented
- 1 generator + noise model
- 1 repair loop with logs
- 1 metrics summary script
- 1 short README describing how to reproduce
