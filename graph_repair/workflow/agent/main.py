import json
import logging
import os
import sys

# Ensure we can import from the root module if run as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import config
#from graph_repair.seed import init_seed
from graph_repair.experiments.evaluator import TailoredEvaluator
from graph_repair.experiments.snapshot import export_snapshot
from graph_repair.synthetic.legacy_generator import Generator
from graph_repair.workflow.app import build_repair_app

# Configure logging to see agent interactions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_inconsistencies(file_path: str = "inconsistencies.txt") -> list[str]:
    # Looking at the repo, the file seems to be inconsistencies.txt 
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    full_path = os.path.join(root_dir, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Inconsistency file not found: {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.read().splitlines() if line.strip()]


def main():
    logger.info("Initializing benchmark for the agentic repair system...")
#    init_seed()    
    # Initialize Generator
    generator = Generator(config.NEO4J_URI, (config.NEO4J_USERNAME, config.NEO4J_PASSWORD))

    logger.info("1. Generating Graph Rules...")
    generator.generate_rules(num_allowed=20, num_disallowed=5)
    generator.export_ontology("ontology_final.json")

    evaluator = TailoredEvaluator(
        config.NEO4J_URI,
        config.NEO4J_USERNAME,
        config.NEO4J_PASSWORD,
        "ontology_final.json",
    )

    logger.info("2. Generating Clean Graph...")
    generator.generate_valid_graph(num_nodes=50)
    snap_gold = evaluator.fetch_snapshot()
    export_snapshot("snapshot_gold.cypher")

    logger.info("3. Injecting Violations...")
    generator.inject_violations()
    snap_messy = evaluator.fetch_snapshot()
    export_snapshot("snapshot_messy.cypher")

    list_of_inconsistencies = load_inconsistencies("inconsistencies.txt")

    logger.info("4. Starting Agent Repair App...")
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
        "iteration_count": 0,
        "repair_status_array": [],
        "prev_repair_status_array": [],
        "current_index": 0,
        "messages": [],
    }
    
    final_state = app.invoke(initial_state, config={"recursion_limit": 1000})

    logger.info("5. Exporting Repaired Snapshot...")
    export_snapshot("snapshot_repaired.cypher")
    
    logger.info("6. Evaluating Results...")
    results = evaluator.evaluate(snap_gold, snap_messy, final_state.get("total_tokens", 0))
    
    logger.info("\n--- AGENTIC SYSTEM BENCHMARK RESULTS ---")
    print(json.dumps(results, indent=4))

    generator.close()


if __name__ == "__main__":
    main()