from _bootstrap import ensure_project_root

ensure_project_root()

import config
from graph_repair.experiments.snapshot import export_snapshot
from graph_repair.synthetic.legacy_generator import Generator


def main():
    print("=== Creating Normal Graph G ===")
    gen = Generator(config.NEO4J_URI, (config.NEO4J_USERNAME, config.NEO4J_PASSWORD))
    try:
        gen.clear_database()
        gen.generate_rules(num_allowed=20, num_disallowed=5)
        gen.export_ontology("ontology_final.json")
        gen.generate_valid_graph(num_nodes=50)
        export_snapshot("snapshot_G.cypher")
    finally:
        gen.close()

    print("\nGraph G successfully created and snapshotted!")


if __name__ == "__main__":
    main()
