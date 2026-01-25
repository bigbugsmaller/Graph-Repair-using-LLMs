# Submission to SIGMOD

## Outline

* Have a clean, consistent graph G  generated from rules/constraints.
* corrupt it with a controlled noise model to G_in
* system outputs G_out  that must satisfy constraints.
* Now you can measure:
  - Validity: does G_out satisfy constraints?
  - Recovery: how close is G_out to G
  - Minimality: how close is G_in to G_out

This lets you fairly evaluate both 'repair correctness' and 'originality retention/minimality of repairs'

---

**Verifier–Proposer–Optimizer loop**

* Verifier: deterministic constraint checker
* Proposer: LLM generates candidate repairs (small, local, justified)
* Optimizer: chooses a set of repairs minimizing cost while satisfying all constraints (exact on small graphs, heuristic on large)
Iterate until feasible or budget exhausted.

Implementation note (Neo4j property graphs):
* Store G, G_in, G_out in Neo4j (nodes + relationships + properties)
* Constraints are Cypher patterns
* Verifier = Cypher queries that detect violations
* Repairs = Cypher updates (DELETE/DETACH/SET/MERGE)

## Problem Definition

* clear class of constraints (e.g., denial constraints, tuple generation dependencies, graph integrity constraints, functional dependencies lifted to graphs, motif constraints, etc.)
* clear definition of inconsistency (pattern violation)
* clear repair action set (add/remove edge, relabel node, merge/split entities, delete node, etc.)
* clear objective (minimum-cost repair) with a cost model
* include property-level edits (properties are first-class in property graphs)

## Data

Synthetic Generator class or standalone script/program should be:
* public (github, eventually), reproducible and parametrized (controlled parameters)
* noise controlled,  mirroring 'plausible' data errors (missing edges, spurious edges, mistyped labels, entity duplication, etc etc)

Note: We need at least one "real" dataset (or a truly convincing argument that real data is unavailable)

## Evaluation

Evaluation metrics need to be "reviewer-proof"

Should report at least these:
* Constraint satisfaction:
  - % constraints satisfied / # violations remaining
  - time to reach feasibility (iterations, tokens, wall clock)
* Repair minimality
  - Graph edit distance (GED) or a weighted edit cost from G_in to G_out
  - Break down by operation type (adds/deletes/attribute edits)
* Fidelity to the clean graph
  - Precision/recall/F1 on edges and labels comparing (G_out vs G)
  - Property-level accuracy (correct/incorrect attribute edits)
  - Structural similarity measures (degree distribution drift, motif counts)
* Optimality gap
  - For small instances, compute the optimal minimum repair via ILP/MaxSAT/ASP
  - Report approximation ratio / gap of our approach vs optimal

Without an optimality anchor, "minimal change" is subjective


### Baselines

We need other baseline comparisons
- Rule-based repair heuristics (greedy fix-by-violation)
- Constraint-solving baselines (ILP/MaxSAT/ASP) on feasible scales
- Existing data cleaning/repair methods (depending on constraint type)
- Graph constraint validation+repair tools (if you use SHACL-like constraints)

For LLM-specific work:
- prompt-only
- tool-augmented (LLM + solver)
- self-consistency / debate / verifier loop
- fine-tuned small model baseline *if feasible*

## Contribution Requirements

For a viable SIGMOD paper, we require at least one or more of the following:

* New formalism for graph inconsistency repair that is practically relevant and computationally grounded (IDK if we have this)
* New algorithm/system: scalable repair with guarantees or strong empirical performance
* Hybrid framework: LLM proposes candidate repairs, symbolic verifier checks constraints, search/optimization chooses minimal-cost repair
* Benchmark: a widely useful benchmark suite with real + synthetic + standard constraints and noise
* Analysis: where LLMs succeed/fail, with error taxonomies and robustness
