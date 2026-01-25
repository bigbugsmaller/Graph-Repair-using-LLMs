from neo4j import GraphDatabase
import logging
from typing import Any, Dict, Optional

class GraphDB:
    def __init__(self, url, user, password):
        if not url or not user or not password:
            raise ValueError(
                "Neo4j connection info missing. Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD."
            )
        try:
            self.driver = GraphDatabase.driver(url, auth=(user, password))
        except Exception as e:
            logging.exception("Failed connection to Neo4j")
            raise


    def close(self):
        driver = getattr(self, "driver", None)
        if driver is None:
            return
        logging.info("Driver closed.")
        driver.close()

    def run_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        if params is None:
            params = {}
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]
