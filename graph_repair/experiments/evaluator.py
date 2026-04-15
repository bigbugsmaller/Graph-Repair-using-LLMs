from __future__ import annotations

import json
from typing import Any

from neo4j import GraphDatabase


class TailoredEvaluator:
    def __init__(self, uri: str, user: str, password: str, ontology_path: str):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            connection_timeout=120.0,
            keep_alive=True,
            max_connection_lifetime=3600,
        )
        with open(ontology_path, "r", encoding="utf-8") as file:
            self.ontology = json.load(file)

    def fetch_snapshot(self):
        nodes = {}
        edges = []
        with self.driver.session() as session:
            node_rows = session.run(
                "MATCH (n) RETURN n.id as id, labels(n)[0] as type, properties(n) as props"
            )
            for record in node_rows:
                props: dict[str, Any] = record["props"] or {}
                nodes[record["id"]] = {
                    "type": record["type"],
                    "x": props.get("x"),
                    "date": str(props.get("date_val")) if props.get("date_val") else None,
                }

            edge_rows = session.run(
                "MATCH (n)-[r]->(m) RETURN n.id as src, type(r) as rel, m.id as tgt, properties(r) as props"
            )
            for record in edge_rows:
                props: dict[str, Any] = record["props"] or {}
                edges.append(
                    {
                        "src": record["src"],
                        "rel": record["rel"],
                        "tgt": record["tgt"],
                        "A1": props.get("A1"),
                    }
                )
        return {"nodes": nodes, "edges": edges}

    def count_violations(self, snapshot):
        violations = 0
        for node_id, data in snapshot["nodes"].items():
            node_edges = [edge for edge in snapshot["edges"] if edge["src"] == node_id]
            rule = self.ontology.get("neighborhood_constraints", {}).get(data["type"], {})
            if rule.get("type") == "max_degree":
                if len(node_edges) > rule.get("limit", 999):
                    violations += 1

        disallowed = self.ontology.get("triples", {}).get("disallowed", [])
        for edge in snapshot["edges"]:
            src_type = snapshot["nodes"].get(edge["src"], {}).get("type")
            tgt_type = snapshot["nodes"].get(edge["tgt"], {}).get("type")
            if [src_type, edge["rel"], tgt_type] in disallowed:
                violations += 1
        return violations

    def calculate_ged(self, snap_a, snap_b):
        nodes_a_struct = set((nid, data["type"]) for nid, data in snap_a["nodes"].items())
        nodes_b_struct = set((nid, data["type"]) for nid, data in snap_b["nodes"].items())

        nodes_removed = len(nodes_a_struct - nodes_b_struct)
        nodes_added = len(nodes_b_struct - nodes_a_struct)
        node_id_dist = (nodes_removed + nodes_added) * 1.0

        nodes_attr_changed = 0
        common_nodes = nodes_a_struct.intersection(nodes_b_struct)
        for nid, _node_type in common_nodes:
            val_a = {key: snap_a["nodes"][nid][key] for key in ["x", "date"]}
            val_b = {key: snap_b["nodes"][nid][key] for key in ["x", "date"]}
            if val_a != val_b:
                nodes_attr_changed += 1

        attr_dist = nodes_attr_changed * 0.2

        edges_a_struct = set((e["src"], e["rel"], e["tgt"]) for e in snap_a["edges"])
        edges_b_struct = set((e["src"], e["rel"], e["tgt"]) for e in snap_b["edges"])

        edges_removed = len(edges_a_struct - edges_b_struct)
        edges_added = len(edges_b_struct - edges_a_struct)
        edge_id_dist = (edges_removed + edges_added) * 0.5

        edges_attr_changed = 0
        common_edges = edges_a_struct.intersection(edges_b_struct)
        for src, rel, tgt in common_edges:
            edge_a = next(e for e in snap_a["edges"] if e["src"] == src and e["rel"] == rel and e["tgt"] == tgt)
            edge_b = next(e for e in snap_b["edges"] if e["src"] == src and e["rel"] == rel and e["tgt"] == tgt)
            if edge_a.get("A1") != edge_b.get("A1"):
                edges_attr_changed += 1

        attr_dist += edges_attr_changed * 0.2
        total_ged = node_id_dist + edge_id_dist + attr_dist

        return {
            "total": total_ged,
            "breakdown": {
                "nodes_added": nodes_added,
                "nodes_removed": nodes_removed,
                "node_attrs_changed": nodes_attr_changed,
                "edges_added": edges_added,
                "edges_removed": edges_removed,
                "edge_attrs_changed": edges_attr_changed,
            },
        }

    def evaluate(self, snap_gold, snap_messy, tokens_used: int):
        snap_out = self.fetch_snapshot()

        ged_noise_obj = self.calculate_ged(snap_gold, snap_messy)
        ged_repair_obj = self.calculate_ged(snap_messy, snap_out)
        ged_final_obj = self.calculate_ged(snap_gold, snap_out)

        ged_noise = ged_noise_obj["total"]
        ged_repair = ged_repair_obj["total"]
        ged_final = ged_final_obj["total"]

        max_possible_ged = len(snap_gold["nodes"]) + (len(snap_gold["edges"]) * 0.5)
        normalized_ged = min(ged_final / max_possible_ged, 1.0) if max_possible_ged > 0 else 0.0
        fidelity_score = 1.0 - normalized_ged

        violations_in = self.count_violations(snap_messy)
        violations_out = self.count_violations(snap_out)

        return {
            "Validity": round((violations_in - violations_out) / violations_in, 4)
            if violations_in > 0
            else 1.0,
            "Fidelity Score (0-1)": round(fidelity_score, 4),
            "Normalized GED (0-1)": round(normalized_ged, 4),
            "Raw GED Remaining": round(ged_final, 2),
            "Minimality (Repair Cost)": round(ged_repair, 2),
            "Optimality Ratio": round(ged_noise / ged_repair, 2) if ged_repair > 0 else 0,
            "Efficiency (Tokens/Fix)": round(tokens_used / (violations_in - violations_out), 2)
            if (violations_in - violations_out) > 0
            else 0,
            "Repair Breakdown": ged_repair_obj["breakdown"],
            "Error Breakdown (Noise)": ged_noise_obj["breakdown"],
        }
