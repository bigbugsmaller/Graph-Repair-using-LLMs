from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import config
from graph_repair.db import GraphDB


def _serialize_property_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [_serialize_property_value(item) for item in value]
    return str(value)


def _fetch_snapshot_payload(db: GraphDB) -> dict[str, Any]:
    node_rows = db.run_query(
        "MATCH (n) RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS props ORDER BY elementId(n)"
    )
    rel_rows = db.run_query(
        """
        MATCH (a)-[r]->(b)
        RETURN elementId(a) AS start_id,
               elementId(b) AS end_id,
               type(r) AS type,
               properties(r) AS props
        ORDER BY start_id, type, end_id
        """
    )

    return {
        "format": "graph_repair_snapshot_v1",
        "nodes": [
            {
                "element_id": row["element_id"],
                "labels": row["labels"],
                "props": {
                    key: _serialize_property_value(value)
                    for key, value in (row["props"] or {}).items()
                },
            }
            for row in node_rows
        ],
        "relationships": [
            {
                "start_id": row["start_id"],
                "end_id": row["end_id"],
                "type": row["type"],
                "props": {
                    key: _serialize_property_value(value)
                    for key, value in (row["props"] or {}).items()
                },
            }
            for row in rel_rows
        ],
    }


def _export_snapshot_without_apoc(db: GraphDB, output_filename: str):
    payload = _fetch_snapshot_payload(db)
    Path(output_filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Snapshot successfully saved to '{output_filename}' using built-in JSON export.")


def export_snapshot(output_filename: str = "snapshot.cypher"):
    db = GraphDB(
        config.NEO4J_URI,
        config.NEO4J_USERNAME,
        config.NEO4J_PASSWORD,
        config.NEO4J_DATABASE,
    )
    query = """
    CALL apoc.export.cypher.all(null, {
        stream: true,
        format: 'cypher-shell'
    })
    YIELD cypherStatements
    RETURN cypherStatements AS data
    """

    print("Extracting database snapshot from Neo4j...")
    try:
        try:
            results = db.run_query(query)
            if results and "data" in results[0]:
                Path(output_filename).write_text(results[0]["data"], encoding="utf-8")
                print(f"Snapshot successfully saved to '{output_filename}'.")
            else:
                print("No data was returned. Is the database empty?")
        except Exception as exc:
            if "apoc.export.cypher.all" not in str(exc):
                raise
            _export_snapshot_without_apoc(db, output_filename)
    finally:
        db.close()


def _quote_cypher_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _to_cypher_literal(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_to_cypher_literal(item) for item in value) + "]"
    if isinstance(value, str):
        if value.startswith("date(") and value.endswith(")"):
            return value
        return _quote_cypher_string(value)
    return _quote_cypher_string(str(value))


def _restore_json_snapshot(db: GraphDB, payload: dict[str, Any], snapshot_filename: str):
    for node in payload.get("nodes", []):
        labels = "".join(f":`{label.replace('`', '``')}`" for label in node.get("labels", []))
        props = dict(node.get("props", {}))
        props["__snapshot_element_id"] = node["element_id"]
        prop_body = ", ".join(
            f"`{key.replace('`', '``')}`: {_to_cypher_literal(value)}"
            for key, value in props.items()
        )
        db.run_query(f"CREATE ({labels} {{ {prop_body} }})")

    for rel in payload.get("relationships", []):
        rel_type = rel["type"].replace("`", "``")
        props = rel.get("props", {})
        prop_body = ", ".join(
            f"`{key.replace('`', '``')}`: {_to_cypher_literal(value)}"
            for key, value in props.items()
        )
        prop_clause = f" {{ {prop_body} }}" if prop_body else ""
        start_id = _to_cypher_literal(rel["start_id"])
        end_id = _to_cypher_literal(rel["end_id"])
        db.run_query(
            f"""
            MATCH (a {{`__snapshot_element_id`: {start_id}}}), (b {{`__snapshot_element_id`: {end_id}}})
            CREATE (a)-[:`{rel_type}`{prop_clause}]->(b)
            """
        )

    db.run_query("MATCH (n) REMOVE n.`__snapshot_element_id`")

    print(f"Snapshot restored from '{snapshot_filename}'.")


def restore_snapshot(snapshot_filename: str):
    snapshot_path = Path(snapshot_filename)
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {snapshot_filename}")

    db = GraphDB(
        config.NEO4J_URI,
        config.NEO4J_USERNAME,
        config.NEO4J_PASSWORD,
        config.NEO4J_DATABASE,
    )
    try:
        db.run_query("MATCH (n) DETACH DELETE n")
        content = snapshot_path.read_text(encoding="utf-8")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            payload = None

        if isinstance(payload, dict) and payload.get("format") == "graph_repair_snapshot_v1":
            _restore_json_snapshot(db, payload, snapshot_filename)
            return

        statements = [statement.strip() for statement in content.split(";") if statement.strip()]
        for statement in statements:
            db.run_query(f"{statement};")
        print(f"Snapshot restored from '{snapshot_filename}'.")
    finally:
        db.close()


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_snapshot(f"snapshot_{timestamp}.cypher")
