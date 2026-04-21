from __future__ import annotations

import logging
from typing import Any

from graph_repair.db import GraphDB


NODE_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output
"""

REL_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS relType, collect({property:property, type:type}) AS properties
RETURN {type: relType, properties: properties} AS output
"""

REL_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
UNWIND other AS other_node
RETURN {start: label, type: property, end: toString(other_node)} AS output
"""


def _escape_identifier(value: str) -> str:
    return value.replace("`", "``")


def _python_type_name(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    return type(value).__name__.upper()


def _collect_node_properties_without_apoc(db: GraphDB) -> dict[str, list[dict[str, str]]]:
    labels = [row["label"] for row in db.run_query("CALL db.labels() YIELD label RETURN label ORDER BY label")]
    node_props: dict[str, list[dict[str, str]]] = {}

    for label in labels:
        safe_label = _escape_identifier(label)
        rows = db.run_query(f"MATCH (n:`{safe_label}`) RETURN properties(n) AS props LIMIT 25")
        prop_types: dict[str, str] = {}
        for row in rows:
            for key, value in row["props"].items():
                prop_types.setdefault(key, _python_type_name(value))

        node_props[label] = [
            {"property": key, "type": prop_types[key]}
            for key in sorted(prop_types)
        ]

    return node_props


def _collect_relationship_properties_without_apoc(db: GraphDB) -> dict[str, list[dict[str, str]]]:
    rel_types = [
        row["relationshipType"]
        for row in db.run_query(
            "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
        )
    ]
    rel_props: dict[str, list[dict[str, str]]] = {}

    for rel_type in rel_types:
        safe_rel_type = _escape_identifier(rel_type)
        rows = db.run_query(f"MATCH ()-[r:`{safe_rel_type}`]->() RETURN properties(r) AS props LIMIT 25")
        prop_types: dict[str, str] = {}
        for row in rows:
            for key, value in row["props"].items():
                prop_types.setdefault(key, _python_type_name(value))

        rel_props[rel_type] = [
            {"property": key, "type": prop_types[key]}
            for key in sorted(prop_types)
        ]

    return rel_props


def _collect_relationship_patterns_without_apoc(db: GraphDB) -> list[dict[str, str]]:
    query = """
    MATCH (a)-[r]->(b)
    RETURN DISTINCT
        head(labels(a)) AS start,
        type(r) AS type,
        head(labels(b)) AS end
    ORDER BY start, type, end
    """
    return [row for row in db.run_query(query) if row["start"] and row["end"]]


def _get_structured_schema_without_apoc(db: GraphDB) -> dict[str, Any]:
    logging.info("APOC schema procedures unavailable; falling back to built-in schema inspection.")
    return {
        "node_props": _collect_node_properties_without_apoc(db),
        "rel_props": _collect_relationship_properties_without_apoc(db),
        "relationships": _collect_relationship_patterns_without_apoc(db),
    }


def get_structured_schema(db: GraphDB) -> dict[str, Any]:
    try:
        node_properties = [item["output"] for item in db.run_query(NODE_PROPERTIES_QUERY)]
        rel_properties = [item["output"] for item in db.run_query(REL_PROPERTIES_QUERY)]
        relationships = [item["output"] for item in db.run_query(REL_QUERY)]
        return {
            "node_props": {el["labels"]: el["properties"] for el in node_properties},
            "rel_props": {el["type"]: el["properties"] for el in rel_properties},
            "relationships": relationships,
        }
    except Exception as exc:
        if "apoc.meta.data" not in str(exc):
            raise
        return _get_structured_schema_without_apoc(db)


def get_schema(structured_schema: dict[str, Any]) -> str:
    def _format_props(props: list[dict[str, Any]]) -> str:
        return ", ".join(f"{prop['property']}: {prop['type']}" for prop in props)

    formatted_node_props = [
        f"{label} {{{_format_props(props)}}}"
        for label, props in structured_schema["node_props"].items()
    ]
    formatted_rel_props = [
        f"{rel_type} {{{_format_props(props)}}}"
        for rel_type, props in structured_schema["rel_props"].items()
    ]
    formatted_rels = [
        f"(:{element['start']})-[:{element['type']}]->(:{element['end']})"
        for element in structured_schema["relationships"]
    ]

    return "\n".join(
        [
            "Node labels and properties:",
            "\n".join(formatted_node_props),
            "Relationship types and properties:",
            "\n".join(formatted_rel_props),
            "The relationships:",
            "\n".join(formatted_rels),
        ]
    )
