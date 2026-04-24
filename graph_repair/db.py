import logging
from typing import Any, Dict, Optional
from neo4j import GraphDatabase


class GraphDB:
    _drivers: dict[tuple[str, str, str], Any] = {}

    def __init__(self, url: str, user: str, password: str, database: Optional[str] = None):
        if not url or not user or not password:
            raise ValueError(
                "Neo4j connection info missing. Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD."
            )

        self.database = database
        cache_key = (url, user, password)
        
        if cache_key in self._drivers:
            self.driver = self._drivers[cache_key]
        else:
            try:
                self.driver = GraphDatabase.driver(
                    url,
                    auth=(user, password),
                    connection_timeout=120.0,
                    keep_alive=True,
                    max_connection_lifetime=3600,
                )
                self._drivers[cache_key] = self.driver
            except Exception:
                logging.exception("Failed connection to Neo4j")
                raise

    def close(self) -> None:
        # We don't close the driver here anymore because it's shared.
        # We might want a dedicated global cleanup later.
        pass

    def close_all(self) -> None:
        """Explicitly close all cached drivers."""
        for driver in self._drivers.values():
            driver.close()
        self._drivers.clear()

    def run_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        if not query or not query.strip():
            logging.warning("Attempted to run an empty query; execution skipped.")
            return []

        if params is None:
            params = {}

        kwargs = {}
        if self.database is not None:
            kwargs["database"] = self.database

        with self.driver.session(**kwargs) as session:
            result = session.run(query, params)
            return [record.data() for record in result]

