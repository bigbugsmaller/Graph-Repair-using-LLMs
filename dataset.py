import random
from neo4j import GraphDatabase

uri="neo4j+s://ab4ea282.databases.neo4j.io"
user="neo4j"
password="fG_j6qXdDmB620AKh0aAawHR32jlTnqxO0M1tNUf2vA"

class FilePatternGenerator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_queries_from_file(self, filename):
        """Reads and executes queries from a specified text file."""
        queries = []
        try:
            with open(filename, 'r') as f:
            
                queries = [line.strip() for line in f if line.strip() and not line.startswith("//")]
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            return []
        
        with self.driver.session() as session:
   
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleaned.")

            
            print(f"Injecting {len(queries)} patterns from {filename}...")
            for i, query in enumerate(queries):
                session.run(query)
                print(f"  - Pattern {i+1} injected.")
        
        return queries

    def add_random_noise(self, noise_count=30):
        """Creates random relationships between existing nodes to add complexity."""
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
                    session.run(f"""
                        MATCH (a), (b) 
                        WHERE id(a) = $id1 AND id(b) = $id2
                        MERGE (a)-[:{rel_type} {{source: 'noise'}}]->(b)
                    """, id1=id1, id2=id2) 

if __name__ == "__main__":
    
    NEO4J_URI = "neo4j+s://ab4ea282.databases.neo4j.io"
    AUTH = ("neo4j", "fG_j6qXdDmB620AKh0aAawHR32jlTnqxO0M1tNUf2vA")

    gen = FilePatternGenerator(NEO4J_URI, AUTH[0], AUTH[1])
    
    
    if gen.run_queries_from_file("patterns.txt"):
        gen.add_random_noise(noise_count=50)
    
    gen.close()
    print("\nAbstract dataset generation complete!")