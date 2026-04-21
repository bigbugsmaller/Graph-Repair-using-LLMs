from __future__ import annotations

import json
import random
from datetime import date, timedelta

from neo4j import GraphDatabase


class Generator:
    """Legacy synthetic generator preserved as a structured module."""

    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.num_node_types = 5
        self.num_rel_types = 4
        self.allowed_patterns = set()
        self.disallowed_patterns = set()
        self.neighborhood_rules = {}
        self.property_constraint = None

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def generate_rules(self, num_allowed=20, num_disallowed=5):
        all_node_types = [f"N{i}" for i in range(1, self.num_node_types + 1)]
        all_rel_types = [f"R{i}" for i in range(1, self.num_rel_types + 1)]

        universe = {
            (src, rel, tgt)
            for src in all_node_types
            for tgt in all_node_types
            for rel in all_rel_types
        }

        self.allowed_patterns = set(random.sample(list(universe), num_allowed))
        remaining = universe - self.allowed_patterns
        self.disallowed_patterns = set(random.sample(list(remaining), num_disallowed))

        active_types = set()
        for src, _rel, tgt in self.allowed_patterns:
            active_types.add(src)
            active_types.add(tgt)

        if active_types:
            target_type = random.choice(list(active_types))
            threshold_val = random.randint(30, 70)
            self.property_constraint = {
                "node_type": target_type,
                "threshold": threshold_val,
            }

        for node_type in all_node_types:
            rand_val = random.random()
            if rand_val < 0.2:
                self.neighborhood_rules[node_type] = {
                    "type": "max_degree",
                    "limit": random.randint(1, 5),
                    "rel_type": random.choice(all_rel_types),
                }
            elif rand_val < 0.5:
                others = [t for t in all_node_types if t != node_type]
                if len(others) >= 2:
                    self.neighborhood_rules[node_type] = {
                        "type": "exclusive",
                        "conflict_pair": random.sample(others, 2),
                        "rel_type": random.choice(all_rel_types),
                    }
            elif rand_val < 0.75:
                others = [t for t in all_node_types if t != node_type]
                if len(others) >= 2:
                    pair = random.sample(others, 2)
                    self.neighborhood_rules[node_type] = {
                        "type": "dependency",
                        "trigger": pair[0],
                        "required": pair[1],
                        "rel_type": random.choice(all_rel_types),
                    }
            else:
                others = [t for t in all_node_types if t != node_type]
                if others:
                    self.neighborhood_rules[node_type] = {
                        "type": "temporal",
                        "target": random.choice(others),
                        "rel_type": random.choice(all_rel_types),
                    }

    def generate_valid_graph(self, num_nodes=80):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            needs_date = set()
            for src_type, rule in self.neighborhood_rules.items():
                if rule["type"] == "temporal":
                    needs_date.add(src_type)
                    needs_date.add(rule["target"])

            needs_prop_x = set()
            if self.property_constraint:
                needs_prop_x.add(self.property_constraint["node_type"])

            node_ids = []
            for index in range(num_nodes):
                node_type = f"N{random.randint(1, self.num_node_types)}"
                uid = f"node_{index}"
                props = [f"id: '{uid}'"]

                if node_type in needs_date:
                    start_dt = date(2000, 1, 1)
                    end_dt = date(2023, 12, 31)
                    delta = end_dt - start_dt
                    date_str = (start_dt + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")
                    props.append(f"date_val: date('{date_str}')")

                if node_type in needs_prop_x:
                    limit = self.property_constraint["threshold"]
                    props.append(f"x: {random.randint(limit + 1, 100)}")

                session.run(f"CREATE (n:{node_type} {{ {', '.join(props)} }})")
                node_ids.append((uid, node_type))

            global_neighbors = {uid: set() for uid, _ in node_ids}

            for src_id, src_type in node_ids:
                max_degree_limit = 999
                exclusive_forbidden = set()
                exclusive_rule = None
                dependency_rule = None
                temporal_rule = None

                if src_type in self.neighborhood_rules:
                    rule = self.neighborhood_rules[src_type]
                    if rule["type"] == "max_degree":
                        max_degree_limit = rule["limit"]
                    elif rule["type"] == "exclusive":
                        exclusive_rule = rule
                    elif rule["type"] == "dependency":
                        dependency_rule = rule
                    elif rule["type"] == "temporal":
                        temporal_rule = rule

                connections_made = 0
                random.shuffle(node_ids)
                for tgt_id, tgt_type in node_ids:
                    if src_id == tgt_id or connections_made >= max_degree_limit:
                        continue
                    if tgt_type in exclusive_forbidden:
                        continue

                    target_is_willing = True
                    if tgt_type in self.neighborhood_rules:
                        tgt_rule = self.neighborhood_rules[tgt_type]
                        if tgt_rule["type"] == "exclusive":
                            pair = tgt_rule["conflict_pair"]
                            if src_type in pair:
                                enemy = pair[1] if src_type == pair[0] else pair[0]
                                if enemy in global_neighbors[tgt_id]:
                                    target_is_willing = False

                    if not target_is_willing:
                        continue

                    possible_rels = [
                        rel for (source, rel, target) in self.allowed_patterns if source == src_type and target == tgt_type
                    ]
                    if not possible_rels or random.random() >= 0.2:
                        continue

                    rel_type = random.choice(possible_rels)
                    if temporal_rule and tgt_type == temporal_rule["target"] and rel_type == temporal_rule["rel_type"]:
                        session.run(
                            f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            WHERE a.date_val <= b.date_val
                            SET a.date_val = b.date_val + duration('P1D')
                            """
                        )
                        session.run(
                            f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            MERGE (a)-[:{rel_type} {{A1: 'active'}}]->(b)
                            """
                        )
                    else:
                        session.run(
                            f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            MERGE (a)-[:{rel_type}]->(b)
                            """
                        )

                    connections_made += 1
                    global_neighbors[src_id].add(tgt_type)
                    global_neighbors[tgt_id].add(src_type)

                    if exclusive_rule and tgt_type in exclusive_rule["conflict_pair"]:
                        pair = exclusive_rule["conflict_pair"]
                        exclusive_forbidden.add(pair[1] if tgt_type == pair[0] else pair[0])

                    if dependency_rule and tgt_type == dependency_rule["trigger"]:
                        req_type = dependency_rule["required"]
                        req_rel = dependency_rule["rel_type"]
                        session.run(
                            f"""
                            MATCH (src {{id: '{src_id}'}})
                            MATCH (partner:{req_type}) WHERE partner.id <> src.id
                            WITH src, partner LIMIT 1
                            MERGE (src)-[:{req_rel}]->(partner)
                            """
                        )
                        global_neighbors[src_id].add(req_type)

    def inject_violations(self):
        violation_types = ["triple", "cardinality", "exclusive", "dependency", "temporal", "property_x"]
        with self.driver.session() as session:
            success_count = 0
            with open("inconsistencies.txt", "w", encoding="utf-8") as file:
                for violation_type in violation_types:
                    result = None
                    inconsistency_query = ""

                    if violation_type == "triple" and self.disallowed_patterns:
                        src, rel, tgt = random.choice(list(self.disallowed_patterns))
                        result = session.run(
                            f"MATCH (a:{src}), (b:{tgt}) WHERE a.id <> b.id WITH a,b LIMIT 1 MERGE (a)-[:{rel}]->(b) RETURN a"
                        )
                        inconsistency_query = f"MATCH (n1:{src})-[r:{rel}]->(n2:{tgt}) RETURN n1, r, n2"

                    elif violation_type == "cardinality":
                        candidates = [k for k, v in self.neighborhood_rules.items() if v["type"] == "max_degree"]
                        if candidates:
                            node_type = random.choice(candidates)
                            rule = self.neighborhood_rules[node_type]
                            overflow = rule["limit"] + 2
                            result = session.run(
                                f"""
                                MATCH (a:{node_type}) WITH a LIMIT 1 MATCH (b) WHERE a <> b
                                WITH a, collect(b)[0..{overflow}] as chosen UNWIND chosen AS b
                                MERGE (a)-[:{rule['rel_type']}]->(b) RETURN a
                                """
                            )
                            inconsistency_query = f"MATCH (n1:{node_type})-[r:{rule['rel_type']}]->(n2) RETURN n1, r, n2"

                    elif violation_type == "exclusive":
                        candidates = [k for k, v in self.neighborhood_rules.items() if v["type"] == "exclusive"]
                        if candidates:
                            node_type = random.choice(candidates)
                            rule = self.neighborhood_rules[node_type]
                            pair_a, pair_b = rule["conflict_pair"]
                            result = session.run(
                                f"""
                                MATCH (a:{node_type}) WITH a LIMIT 1
                                MATCH (t1:{pair_a}), (t2:{pair_b}) WITH a,t1,t2 LIMIT 1
                                MERGE (a)-[:{rule['rel_type']}]->(t1)
                                MERGE (a)-[:{rule['rel_type']}]->(t2)
                                RETURN a
                                """
                            )
                            inconsistency_query = (
                                f"MATCH (n1:{node_type})-[r1:{rule['rel_type']}]->(n2:{pair_a}), "
                                f"(n1)-[r2:{rule['rel_type']}]->(n3:{pair_b}) RETURN n1, r1, n2, r2, n3"
                            )

                    elif violation_type == "dependency":
                        candidates = [k for k, v in self.neighborhood_rules.items() if v["type"] == "dependency"]
                        if candidates:
                            node_type = random.choice(candidates)
                            rule = self.neighborhood_rules[node_type]
                            result = session.run(
                                f"""
                                MATCH (a:{node_type}), (b:{rule['trigger']}) WHERE a.id <> b.id WITH a, b LIMIT 1
                                MERGE (a)-[:{rule['rel_type']}]->(b) WITH a
                                OPTIONAL MATCH (a)-[r]->(c:{rule['required']}) DELETE r
                                RETURN a
                                """
                            )
                            inconsistency_query = f"MATCH (n1:{node_type})-[r:{rule['rel_type']}]->(n2:{rule['trigger']}) RETURN n1, r, n2"

                    elif violation_type == "temporal":
                        result = session.run(
                            """
                            MATCH (a)-[r {A1: 'active'}]->(b)
                            WITH a, b LIMIT 1
                            SET a.date_val = b.date_val - duration('P10D')
                            RETURN a
                            """
                        )
                        inconsistency_query = "MATCH (a)-[r {A1: 'active'}]->(b) WHERE a.date_val <= b.date_val RETURN a, r, b"

                    elif violation_type == "property_x" and self.property_constraint:
                        target_type = self.property_constraint["node_type"]
                        threshold = self.property_constraint["threshold"]
                        result = session.run(
                            f"""
                            MATCH (n:{target_type})
                            WHERE n.x > {threshold}
                            WITH n LIMIT 1
                            SET n.x = {threshold} - 10
                            RETURN n
                            """
                        )
                        inconsistency_query = f"MATCH (n:{target_type}) WHERE n.x <= {threshold} RETURN n"

                    if result and result.peek():
                        file.write(f"{inconsistency_query}\n")
                        success_count += 1

            print(f"Finished. Total violations injected: {success_count}/6")

    def export_ontology(self, filename="ontology_final.json"):
        data = {
            "triples": {
                "allowed": [list(pattern) for pattern in self.allowed_patterns],
                "disallowed": [list(pattern) for pattern in self.disallowed_patterns],
            },
            "neighborhood_constraints": self.neighborhood_rules,
            "property_constraint": self.property_constraint,
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load_ontology(self, filename="ontology_final.json"):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        self.allowed_patterns = set(tuple(pattern) for pattern in data["triples"]["allowed"])
        self.disallowed_patterns = set(tuple(pattern) for pattern in data["triples"]["disallowed"])
        self.neighborhood_rules = data["neighborhood_constraints"]
        self.property_constraint = data.get("property_constraint")

