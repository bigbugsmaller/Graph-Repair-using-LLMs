# Submission to ACL Venues

## High-Level Goal

Study and characterize the *reasoning behavior of large language models* while repairing abstract structured data (graphs) under consistency constraints, with a particular focus on:

* faithfulness / minimal intervention
* hallucination and over-correction
* iterative self-repair dynamics
* robustness to spurious or non-existent inconsistencies

The goal is **not** to propose an optimal graph repair system, but to *diagnostically evaluate and analyze LLM reasoning under structured constraints*.

In this project, graphs are **property graphs** stored in Neo4j:
* nodes have labels and properties
* relationships have types and properties
* constraints and repairs are expressed in Cypher

## Outline

* Generate an abstract, consistent graph G from a set of symbolic rules/constraints
* Corrupt G using a controlled noise process to obtain G_in
* Provide G_in and the constraint specification to the LLM
* The model iteratively produces a repaired graph G_out intended to satisfy constraints
* Verification and repairs are implemented as Cypher queries over a Neo4j property graph

Key framing:
* G is a **reference graph**, not a hidden ground truth
* The task evaluates whether models can:
  - detect genuine violations
  - avoid hallucinating non-existent ones
  - make minimal, well-justified changes

## Core Research Questions

1. Can LLMs correctly reason about abstract graph constraints?
2. Do LLMs over-edit when asked to enforce consistency?
3. How robust are LLMs to false or spurious inconsistency cues?
4. How does iterative verification and feedback affect repair quality?
5. What kinds of systematic failures or hallucinations arise?


## Model Interaction Loop (Reasoning-Centric)

**Verifier–Proposer Loop** (Optimizer optional / implicit)

* Verifier:
  - deterministic constraint checker
  - used to provide feedback, not guarantees

* Proposer:
  - LLM proposes local repairs with natural language justification
  - optionally produces intermediate reasoning traces

* Iteration:
  - model revises output based on verifier feedback
  - stops when no violations are detected or budget is exhausted

Note:
* Optimization is treated as *behavioral preference*, not algorithmic optimality.
* Any explicit solver is used only as a diagnostic aid, not a primary contribution.

---

## Problem Definition

* Constraints:
  - abstract, symbolic graph constraints (e.g., forbidden motifs, type consistency, relational patterns)
  - clearly specified but intentionally domain-agnostic

* Inconsistency:
  - violation of a declared constraint
  - includes both real and injected “non-existent” inconsistencies

* Repair actions:
  - add/remove edge
  - relabel node
  - local structural edits
  - add/remove properties (property graph–specific)

* Objective (informal):
  - satisfy constraints while minimizing unnecessary changes

Emphasis on clarity and interpretability over theoretical completeness

## Data

### Synthetic Graph Generator

Primary role: **diagnostic testbed**, not realism

Properties:
* fully reproducible and parameterized
* adjustable graph size, density, constraint complexity
* controllable noise types:
  - missing edges
  - spurious edges
  - incorrect labels
  - entity duplication
* ability to inject **false inconsistency prompts**

Justification:
* abstract data isolates reasoning ability from domain knowledge

Optional:
* one small real or semi-real dataset for sanity checking (not central)

## Neo4j / Property Graph Alignment

* Represent all graphs in Neo4j (Aura or local)
* Express constraints as Cypher patterns (e.g., forbidden motifs, label consistency)
* Verifier = deterministic Cypher queries that detect violations
* Repairs = Cypher updates (MATCH/DELETE/DETACH/SET/MERGE)
* Log each repair with a rationale and the exact Cypher used

Suggested structure:
* `generator.py`: build G and inject controlled noise into G_in
* `verifier.py`: a library of Cypher checks (one per constraint)
* `proposer.py`: prompt the LLM to propose a minimal repair
* `runner.py`: iterative loop + logging + metrics


## Evaluation Metrics

Evaluation is *model-centric and behavioral*, not optimality-centric

### Constraint Reasoning Accuracy

* True positive rate: correctly identified real violations
* False positive rate: hallucinated violations
* Precision / Recall on inconsistency detection

### Faithfulness / Minimal Intervention

* % of nodes/edges modified
* Graph edit distance between G_in and G_out
* Over-correction vs under-correction rate

Interpretation:
* measures conservatism and respect for input structure

### Iterative Reasoning Dynamics

* Number of iterations to convergence
* Stability across iterations
* Sensitivity to verifier feedback
* Error accumulation vs correction trends

### Robustness Analysis

* Performance as noise level increases
* Performance under spurious inconsistency injection
* Sensitivity to constraint phrasing

### Qualitative Analysis (Critical)

* Case studies of:
  - correct minimal repairs
  - catastrophic over-editing
  - hallucinated justifications
* Analysis of model explanations vs actual edits
* Error taxonomy (e.g., deletion bias, pattern overgeneralization)

## Baselines (ACL-Appropriate)

### Model Baselines
* Multiple LLMs (e.g., GPT-style vs open models)
* Prompt-only vs structured prompting
* With vs without verifier feedback
* With vs without intermediate reasoning

### Non-LLM Baselines (Lightweight)
* Simple greedy rule-based repair
* Random or minimal-change heuristics

Purpose:
* contextualize LLM behavior, not to prove superiority

## Contribution Requirements

For an ACL submission, the paper should claim one or more of:

* A controlled benchmark for evaluating **faithfulness and hallucination** in structured LLM reasoning
* An empirical study of **iterative self-repair behaviors** in LLMs
* A systematic analysis of **over-correction and false-positive reasoning** in abstract constraint satisfaction
* Insights into how verifier feedback affects LLM reasoning trajectories
