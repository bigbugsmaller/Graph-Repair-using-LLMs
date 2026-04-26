from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from neo4j import GraphDatabase


class GraphDB:
    """Small Neo4j wrapper used across repair and experiment flows."""

    def __init__(self, url: str, user: str, password: str, database: str = None):
        if not url or not user or not password:
            raise ValueError(
                "Neo4j connection info missing. Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD."
            )

        self.database = database
        try:
            self.driver = GraphDatabase.driver(
                url,
                auth=(user, password),
                connection_timeout=120.0,
                keep_alive=True,
                max_connection_lifetime=3600,
            )
        except Exception:
            logging.exception("Failed connection to Neo4j")
            raise

    def close(self) -> None:
        driver = getattr(self, "driver", None)
        if driver is None:
            return
        logging.info("Driver closed.")
        driver.close()

    def run_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        if not query or not query.strip():
            logging.warning("Attempted to run an empty query; execution skipped.")
            return []

        if params is None:
            params = {}

        session_kwargs = {}
        if self.database:
            session_kwargs["database"] = self.database

        with self.driver.session(**session_kwargs) as session:
            result = session.run(query, params)
            return [record.data() for record in result]

