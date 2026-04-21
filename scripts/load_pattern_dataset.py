import random
from pathlib import Path

from _bootstrap import ensure_project_root

ensure_project_root()

import config
from neo4j import GraphDatabase
from graph_repair.seed import init_seed

init_seed()


class FilePatternGenerator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_queries_from_file(self, filename):
        """Read and execute queries from a specified text file."""
        queries = []
        try:
            with open(filename, "r", encoding="utf-8") as file:
                queries = [line.strip() for line in file if line.strip() and not line.startswith("//")]
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            return []

        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleaned.")

            print(f"Injecting {len(queries)} patterns from {filename}...")
            for index, query in enumerate(queries, start=1):
                session.run(query)
                print(f"  - Pattern {index} injected.")

        return queries

    def add_random_noise(self, noise_count=30):
        """Create random relationships between existing nodes to add complexity."""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN id(n) AS node_id")
            node_ids = [record["node_id"] for record in result]

            if len(node_ids) < 2:
                print("Not enough nodes to add noise.")
                return

            print(f"Adding {noise_count} random noise relationships...")
            for _ in range(noise_count):
                id1 = random.choice(node_ids)
                id2 = random.choice(node_ids)
                rel_type = f"NOISE_{random.randint(1, 5)}"

                if id1 != id2:
                    session.run(
                        f"""
                        MATCH (a), (b)
                        WHERE id(a) = $id1 AND id(b) = $id2
                        MERGE (a)-[:{rel_type} {{source: 'noise'}}]->(b)
                        """,
                        id1=id1,
                        id2=id2,
                    )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    patterns_file = project_root / "data" / "patterns.txt"

    generator = FilePatternGenerator(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    if generator.run_queries_from_file(str(patterns_file)):
        generator.add_random_noise(noise_count=50)
    generator.close()
    print("\nAbstract dataset generation complete!")
