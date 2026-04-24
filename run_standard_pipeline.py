import config
from database import Neo4jDatabase
from graph_repair.synthetic.rules_maker import OntologyGenerator
from graph_repair.synthetic.gen_valid import Generator
from graph_repair.synthetic.injector import ViolationInjector

def main():
    # 1. Initialize the Database
    # This is where 'db' comes from!
    db = Neo4jDatabase(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    
    # 2. Generate the Rules
    # This is where 'ontology' comes from!
    ontology = OntologyGenerator()
    ontology.generate_rules(num_allowed=20, num_disallowed=5)
    ontology.export_ontology("ontology_final.json")
    
    # 3. Generate Valid Graph
    # We "pass" the db and ontology into the Generator here
    gen = Generator(db, ontology)
    gen.generate_valid_graph(num_nodes=config.NUM_NODES)
    
    # 4. Inject Violations
    # We also "pass" them into the Injector here
    injector = ViolationInjector(db, ontology)
    injector.inject_violations()
    
    db.close()
    print("\n[Complete] Standard modular pipeline finished.")

if __name__ == "__main__":
    main()
