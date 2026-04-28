import sys
import os
# Add the project root to sys.path so it can find config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
from dotenv import load_dotenv
from graph_repair.db import GraphDB
from graph_repair.synthetic.overlap_rules_maker import OverlapOntologyGenerator
from graph_repair.synthetic.overlap_gen_valid import OverlapGenerator
from graph_repair.synthetic.overlap_injector import OverlapViolationInjector

def run_pipeline():
    """
    This is the main script that runs the entire overlapping graph simulation.
    
    It does three things in order:
        1. Creates the rulebook (Ontology).
        2. Builds a massive valid graph that follows those rules perfectly.
        3. Purposefully breaks the graph at specific "Hub" nodes to create a puzzle 
           for the AI agent to solve.
    """
    # Loads variables from .env
    load_dotenv()
    
    # Initialize DB
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    db = GraphDB(uri, username, password)
    
    # 1. Generate Rules (Ontology)
    print("Step 1: Generating Overlapping Ontology...")
    onto = OverlapOntologyGenerator()
    onto.generate_rules(num_allowed=20, num_disallowed=5)
    onto.export_ontology("ontology_overlap.json")
    
    # 2. Generate Valid Graph
    print("\nStep 2: Generating Valid Graph...")
    gen = OverlapGenerator(db, onto)
    gen.generate_valid_graph(num_nodes=config.NUM_NODES)
    
    # 3. Inject Overlapping Violations
    print("\nStep 3: Injecting Hub-Anchored Overlapping Violations...")
    injector = OverlapViolationInjector(db, onto)
    injector.inject_overlapping_violations()
    
    db.close()
    print("\nPipeline complete.")

if __name__ == "__main__":
    run_pipeline()
