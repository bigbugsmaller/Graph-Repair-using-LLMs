from _bootstrap import ensure_project_root

ensure_project_root()

import config
from graph_repair.experiments.snapshot import export_snapshot
from graph_repair.synthetic.legacy_generator import Generator


def main():
    print("=== Injecting EVERY Type of Inconsistency (Graph G_all_in) ===")
    gen = Generator(config.NEO4J_URI, (config.NEO4J_USERNAME, config.NEO4J_PASSWORD))
    try:
        gen.load_ontology("ontology_final.json")
        gen.inject_violations()
        export_snapshot("snapshot_G_all_in.cypher")
    finally:
        gen.close()

    print("\nGraph G_all_in successfully created and snapshotted!")


if __name__ == "__main__":
    main()
