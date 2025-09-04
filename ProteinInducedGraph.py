import random
import csv
import sys
from neo4j import GraphDatabase

from Inconsistencies import create_artificial_textmining_inconsistencies

csv.field_size_limit(sys.maxsize)

uri = "bolt://localhost:7687"
username = "neo4j"
password = "graph123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def createRelationship(graph, parameter, foreignkey):
    with open("proteinLinks.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if foreignkey in row and parameter in row:  
                if row[foreignkey] in graph:
                    graph[row[foreignkey]].append(row[parameter])
                    
    
                    if int(row["combined_score"]) > 300:
                        query = """
                        MERGE (p1:Protein {id: $id1})
                        MERGE (p2:Protein {id: $id2})
                        MERGE (p1)-[r:LINKS]->(p2)
                        ON CREATE SET r.combined_score = $score
                        ON MATCH SET r.combined_score = $score
                        """
                        with driver.session() as session:
                            session.run(query, {
                                "id1": row[foreignkey],
                                "id2": row[parameter],
                                "score": int(row["combined_score"])
                            })



def textmining(graph):
    
    with open("proteinLinks.csv","r") as file:
        reader=csv.DictReader(file)
        for row in reader:
            if row["protein1"] in graph:

            
                id1=row["protein1"]
                id2=row["protein2"]
                
                with driver.session() as session:
                    q = """
            MERGE (p1:Protein {id: $id1})
            MERGE (p2:Protein {id: $id2})
            MERGE (p1)-[r:textmining]->(p2)
            ON CREATE SET r.textmining_score = $r1
            ON MATCH SET r.textmining_score = $r1
            """
                    session.run(q,{"id1":id1,"id2":id2,"r1":row["textmining"]})

def experimental(graph):
    
    with open("proteinLinks.csv","r") as file:
        reader=csv.DictReader(file)
        for row in reader:
            if row["protein1"] in graph:

                id1=row["protein1"]
                id2=row["protein2"]
                
                with driver.session() as session:
                    q = """
            MERGE (p1:Protein {id: $id1})
            MERGE (p2:Protein {id: $id2})
            MERGE (p1)-[r:experimental]->(p2)
            ON CREATE SET r.experimental_score = $r1
            ON MATCH SET r.experimental_score = $r1
            """
                    session.run(q,{"id1":id1,"id2":id2,"r1":row["experimental"]})

def database(graph):

    with open("proteinLinks.csv","r") as file:
        reader=csv.DictReader(file)
        for row in reader:
            if row["protein1"] in graph:

                id1=row["protein1"]
                id2=row["protein2"]
                
                with driver.session() as session:
                    q = """
            MERGE (p1:Protein {id: $id1})
            MERGE (p2:Protein {id: $id2})
            MERGE (p1)-[r:database]->(p2)
            ON CREATE SET r.database_score = $r1
            ON MATCH SET r.database_score = $r1
            """
                    session.run(q,{"id1":id1,"id2":id2,"r1":row["database"]})

def randBaseNode(fk, limit, filename):
    graph = {}
    
    counter, finalStop = 0, 0

    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if finalStop >= 1000:   
                break

            if random.choice([True, False]) and counter < limit:
                if row[fk] not in graph:
                    graph[row[fk]] = []
                    with driver.session() as session:
                        query = """
                        MERGE (d:Protein {id: $id,desription:$description}) 
                        """
                        session.run(query, {"id": row["id"],"description":row["annotation"]})
                counter += 1

            finalStop += 1

    return graph

if __name__ == "__main__":

    graph = randBaseNode("id", 10, "proteinInfo.csv")

    createRelationship(graph, "protein2", "protein1") 
    textmining(graph)
    experimental(graph)
    database(graph)
    create_artificial_textmining_inconsistencies(1)

    print(graph)
    driver.close()
