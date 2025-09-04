import random
import string
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "graph123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def tweakDescription(graph):
    if not graph:
        return graph 

    graphNodes = list(graph.keys())
    val = random.choice(graphNodes)
    s = graph[val]

    if not s: 
        return graph
    
    i = random.randrange(len(s))

    letters = string.ascii_lowercase
    new_char = random.choice(letters)
    if s[i].isupper():
        new_char = new_char.upper()

    s_list = list(s)
    s_list[i] = new_char
    new_s = "".join(s_list)

    with driver.session() as session:
        query = """
        MERGE (p:Protein {id: $id})
        SET p.description = $description
        SET p:InconsistenProtein
        """
        session.run(query, {"id": val, "description": new_s})
        print("Original:",s)
        print("Changed:",new_s)

    return graph


def create_artificial_textmining_inconsistencies(limit):
    with driver.session() as session:
        result = session.run("""
        MATCH (p1:Protein)-[t:textmining]->(p2:Protein)
        RETURN p1.id AS id1, p2.id AS id2, t.textmining_score AS tscore
        LIMIT 100
        """)

        candidates = [record for record in result]
        if not candidates:
            print("No candidates found for inconsistencies.")
            return

        chosen = random.sample(candidates, min(limit, len(candidates)))

        for record in chosen:
            id1, id2 = record["id1"], record["id2"]

            session.run("""
            MATCH (p1:Protein {id: $id1})-[t:textmining]->(p2:Protein {id: $id2})
            SET t.textmining_score = 900

            MERGE (p1)-[d:database]->(p2)
            SET d.database_score = 50

            MERGE (p1)-[e:experimental]->(p2)
            SET e.experimental_score = 50

            MERGE (p1)-[r:INCONSISTENT]->(p2)
            ON CREATE SET r.reason = 'Artificial: High textmining, low database/experimental',
                          r.textmining_score = 900,
                          r.database_score = 50,
                          r.experimental_score = 50
            """, {"id1": id1, "id2": id2})

        print(f"Artificially created {len(chosen)} textmining inconsistencies.")


# #have to add more 1.edge score cases;
#                   2.databaseScores>experimentalScores
#                 3 . duplicates detection 
#         4 .non overlapping aliases 
        5 .