from neo4j import GraphDatabase

class GraphDB:
    def __init__(self, url, user, password):
        self.driver = GraphDatabase.driver(url, auth=(user, password))
        print("The Graph Database has been started.")

    def close(self):
        self.driver.close()
        print("\nDriver Closed.")

    def run_query(self, query, params={}):
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]