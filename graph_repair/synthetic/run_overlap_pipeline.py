import config
from graph_repair.db import GraphDB
from graph_repair.synthetic.overlap_rules_maker import OverlapOntologyGenerator
from graph_repair.synthetic.overlap_gen_valid import OverlapGenerator
from graph_repair.synthetic.overlap_injector import OverlapViolationInjector

def run_pipeline():
    # Initialize DB
    db = GraphDB(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    
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
