from __future__ import annotations

import json
from pathlib import Path

import config
from graph_repair.experiments.evaluator import TailoredEvaluator
from graph_repair.experiments.snapshot import export_snapshot
from graph_repair.synthetic.legacy_generator import Generator
from graph_repair.workflow.app import build_repair_app


def load_inconsistencies(file_path: str = "inconsistencies.txt") -> list[str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Inconsistency file not found: {file_path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_experiment():
    generator = Generator(config.NEO4J_URI, (config.NEO4J_USERNAME, config.NEO4J_PASSWORD))

    print("Generating Graph Rules...")
    generator.generate_rules(num_allowed=20, num_disallowed=5)
    generator.export_ontology("ontology_final.json")

    evaluator = TailoredEvaluator(
        config.NEO4J_URI,
        config.NEO4J_USERNAME,
        config.NEO4J_PASSWORD,
        "ontology_final.json",
    )

    print("Generating Clean Graph...")
    generator.generate_valid_graph(num_nodes=50)
    snap_gold = evaluator.fetch_snapshot()
    export_snapshot("snapshot_gold.cypher")

    print("Injecting Violations...")
    generator.inject_violations()
    snap_messy = evaluator.fetch_snapshot()
    export_snapshot("snapshot_messy.cypher")

    list_of_inconsistencies = load_inconsistencies()

    print("Starting Agent Repair...")
    app = build_repair_app()
    initial_state = {
        "login_url": config.NEO4J_URI,
        "login_user": config.NEO4J_USERNAME,
        "login_password": config.NEO4J_PASSWORD,
        "list_of_inconsistencies": list_of_inconsistencies,
        "database_description": "",
        "total_tokens": 0,
        "results": [],
        "query": "",
        "status": "",
        "cycle_count": 0,
        "repairs": "",
    }
    final_state = app.invoke(initial_state)

    export_snapshot("snapshot_repaired.cypher")
    results = evaluator.evaluate(snap_gold, snap_messy, final_state.get("total_tokens", 0))
    print("\n--- EXPERIMENT RESULTS ---")
    print(json.dumps(results, indent=4))

    generator.close()
    return results
