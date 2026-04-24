import random
import config

class OverlapViolationInjector:
    def __init__(self, db, ontology):
        self.db = db
        self.ontology = ontology

    def _score_hub_types(self):
        all_node_types = [f"N{i}" for i in range(1, config.NUM_NODE_TYPES + 1)]
        scores = {nt: 0 for nt in all_node_types}

        for nt, rule in self.ontology.neighborhood_rules.items():
            if rule["type"] == "max_degree":
                scores[nt] += 2
            elif rule["type"] == "exclusive":
                scores[nt] += 3
            elif rule["type"] == "dependency":
                scores[nt] += 2
                scores[rule["trigger"]]  += 3
            elif rule["type"] == "comparison":
                scores[nt] += 2
                scores[rule["target"]] += 3

        if self.ontology.property_constraint:
            scores[self.ontology.property_constraint["node_type"]] += 3

        for (s, _, t) in self.ontology.disallowed_patterns:
            scores[s] += 1
            scores[t] += 1

        return scores

    def inject_overlapping_violations(self):
        print(f"\nInjecting {config.NUM_HUBS} hub-anchored overlapping violation sets...")
        
        scores = self._score_hub_types()
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_hub_types = [t for t, s in sorted_types[:config.NUM_HUBS]]
        
        queries = []
        
        # Step 1: Collect hubs
        hub_data = [] # List of (hub_type, hub_id)
        for hub_type in top_hub_types:
            rec = self.db.run_query(f"MATCH (h:{hub_type}) RETURN h.id AS nid ORDER BY rand() LIMIT 1")
            if rec:
                hub_id = rec[0]["nid"]
                hub_data.append((hub_type, hub_id))
                print(f"  Selected Hub: {hub_id} ({hub_type})")

        # Step 2: Batch Property X Violations
        if self.ontology.property_constraint:
            constraint = self.ontology.property_constraint
            target_type = constraint["node_type"]
            thr = constraint["threshold"]
            op = constraint.get("operator", ">")
            
            # Find relevant hubs of this type
            relevant_hubs = [h_id for h_type, h_id in hub_data if h_type == target_type]
            if relevant_hubs:
                if op == ">":
                    self.db.run_query(f"""
                        UNWIND $ids AS h_id
                        MATCH (h:{target_type} {{id: h_id}})
                        SET h.x = {thr} - {config.PROPERTY_VIOLATION_OFFSET}
                    """, params={"ids": relevant_hubs})
                    for h_id in relevant_hubs:
                        queries.append(f"MATCH (h:{target_type} {{id: '{h_id}'}}) WHERE h.x <= {thr} RETURN h")
                        print(f"  [V1 ✓] property_x (op:>) → hub {h_id}")
                else:
                    self.db.run_query(f"""
                        UNWIND $ids AS h_id
                        MATCH (h:{target_type} {{id: h_id}})
                        SET h.x = {thr} + {config.PROPERTY_VIOLATION_OFFSET}
                    """, params={"ids": relevant_hubs})
                    for h_id in relevant_hubs:
                        queries.append(f"MATCH (h:{target_type} {{id: '{h_id}'}}) WHERE h.x >= {thr} RETURN h")
                        print(f"  [V1 ✓] property_x (op:<) → hub {h_id}")

        # Step 3: Batch Exclusive Violations
        # Group hubs by their specific exclusive rule parameters
        for hub_type, hub_id in hub_data:
            hub_rule = self.ontology.neighborhood_rules.get(hub_type)
            if hub_rule and hub_rule["type"] == "exclusive":
                p1, p2 = hub_rule["conflict_pair"]
                self.db.run_query(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}})
                    MATCH (t1:{p1}), (t2:{p2})
                    WHERE t1.id <> h.id AND t2.id <> h.id AND t1.id <> t2.id
                    WITH h, t1, t2 LIMIT 1
                    MERGE (h)-[:{hub_rule['rel_type']}]->(t1)
                    MERGE (h)-[:{hub_rule['rel_type']}]->(t2)
                """)
                queries.append(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r1:{hub_rule['rel_type']}]->(n2:{p1}), (h)-[r2:{hub_rule['rel_type']}]->(n3:{p2}) RETURN h, r1, n2, r2, n3")
                print(f"  [V2 ✓] exclusive    → hub {hub_id}")

        # Step 4: Batch Triple Violations
        for hub_type, hub_id in hub_data:
            hub_src_patterns = [(s, r, t) for (s, r, t) in self.ontology.disallowed_patterns if s == hub_type]
            if hub_src_patterns:
                _, rel, t = random.choice(hub_src_patterns)
                self.db.run_query(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}}), (tgt:{t})
                    WHERE h.id <> tgt.id WITH h, tgt LIMIT 1
                    MERGE (h)-[:{rel}]->(tgt)
                """)
                queries.append(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r:{rel}]->(tgt:{t}) RETURN h, r, tgt")
                print(f"  [V3 ✓] triple       → hub {hub_id}")

        # Step 5: Batch Comparison Violations
        for hub_type, hub_id in hub_data:
            hub_rule = self.ontology.neighborhood_rules.get(hub_type)
            # hub as source or target
            # (Matches Case A and B from before)
            comp_src_type, comp_rule = next(
                ((nt, r) for nt, r in self.ontology.neighborhood_rules.items()
                 if r["type"] == "comparison" and r["target"] == hub_type),
                (None, None)
            )
            if comp_rule is None and hub_rule and hub_rule["type"] == "comparison":
                comp_src_type = hub_type
                comp_rule = hub_rule

            if comp_rule:
                if comp_src_type != hub_type: # H is target
                    self.db.run_query(f"""
                        MATCH (src:{comp_src_type}), (h:{hub_type} {{id: '{hub_id}'}})
                        WHERE src.id <> h.id AND src.prop IS NOT NULL AND h.prop IS NOT NULL
                        WITH src, h LIMIT 1
                        MERGE (src)-[:{comp_rule['rel_type']} {{A1: 'active'}}]->(h)
                        SET src.prop = h.prop - {config.COMPARISON_VIOLATION_OFFSET}
                    """)
                    queries.append(f"MATCH (src:{comp_src_type})-[r {{A1: 'active'}}]->(h:{hub_type} {{id: '{hub_id}'}}) WHERE src.prop <= h.prop RETURN src, r, h")
                    print(f"  [V4 ✓] comparison    → hub {hub_id} (target)")
                else: # H is source
                    self.db.run_query(f"""
                        MATCH (h:{hub_type} {{id: '{hub_id}'}}), (tgt:{comp_rule['target']})
                        WHERE h.id <> tgt.id AND h.prop IS NOT NULL AND tgt.prop IS NOT NULL
                        WITH h, tgt LIMIT 1
                        MERGE (h)-[:{comp_rule['rel_type']} {{A1: 'active'}}]->(tgt)
                        SET h.prop = tgt.prop - {config.COMPARISON_VIOLATION_OFFSET}
                    """)
                    queries.append(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r {{A1: 'active'}}]->(tgt:{comp_rule['target']}) WHERE h.prop <= tgt.prop RETURN h, r, tgt")
                    print(f"  [V4 ✓] comparison    → hub {hub_id} (source)")

        # Step 6: Batch Dependency Violations
        for hub_type, hub_id in hub_data:
            hub_rule = self.ontology.neighborhood_rules.get(hub_type)
            dep_src_type, dep_rule = next(
                ((nt, r) for nt, r in self.ontology.neighborhood_rules.items()
                 if r["type"] == "dependency" and r["trigger"] == hub_type),
                (None, None)
            )
            if dep_rule is None and hub_rule and hub_rule["type"] == "dependency":
                dep_src_type = hub_type
                dep_rule = hub_rule
            
            if dep_rule:
                if dep_src_type != hub_type: # H is trigger
                    dep_rec = self.db.run_query(f"MATCH (dep:{dep_src_type}), (h:{hub_type} {{id: '{hub_id}'}}) WHERE dep.id <> h.id AND NOT (dep)-[:{dep_rule['rel_type']}]->(h) RETURN dep.id AS did LIMIT 1")
                    if dep_rec:
                        did = dep_rec[0]["did"]
                        self.db.run_query(f"MATCH (dep:{dep_src_type} {{id: '{did}'}}), (h:{hub_type} {{id: '{hub_id}'}}) MERGE (dep)-[:{dep_rule['rel_type']}]->(h)")
                        self.db.run_query(f"MATCH (dep:{dep_src_type} {{id: '{did}'}})-[r]->(req:{dep_rule['required']}) DELETE r")
                        queries.append(f"MATCH (dep:{dep_src_type})-[r:{dep_rule['rel_type']}]->(h:{hub_type} {{id: '{hub_id}'}}) WHERE NOT (dep)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']}) RETURN dep, r, h")
                        print(f"  [V5 ✓] dependency   → hub {hub_id} (trigger)")
                else: # H is source
                    trig_rec = self.db.run_query(f"MATCH (h:{hub_type} {{id: '{hub_id}'}}), (trig:{dep_rule['trigger']}) WHERE h.id <> trig.id AND NOT (h)-[:{dep_rule['rel_type']}]->(trig) RETURN trig.id AS tid LIMIT 1")
                    if trig_rec:
                        tid = trig_rec[0]["tid"]
                        self.db.run_query(f"MATCH (h:{hub_type} {{id: '{hub_id}'}}), (trig:{dep_rule['trigger']} {{id: '{tid}'}}) MERGE (h)-[:{dep_rule['rel_type']}]->(trig)")
                        self.db.run_query(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r]->(req:{dep_rule['required']}) DELETE r")
                        queries.append(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r:{dep_rule['rel_type']}]->(trig:{dep_rule['trigger']}) WHERE NOT (h)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']}) RETURN h, r, trig")
                        print(f"  [V5 ✓] dependency   → hub {hub_id} (source)")

        # Step 7: Batch Cardinality Violations
        for hub_type, hub_id in hub_data:
            hub_rule = self.ontology.neighborhood_rules.get(hub_type)
            if hub_rule and hub_rule["type"] == "max_degree":
                overflow = hub_rule["limit"] + config.CARDINALITY_OVERFLOW_OFFSET
                self.db.run_query(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}})
                    MATCH (b) WHERE h <> b
                    WITH h, collect(b)[0..{overflow}] AS chosen UNWIND chosen AS b
                    MERGE (h)-[:{hub_rule['rel_type']}]->(b)
                """)
                queries.append(f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r:{hub_rule['rel_type']}]->(n) WITH h, count(r) AS deg WHERE deg > {hub_rule['limit']} RETURN h")
                print(f"  [V6 ✓] cardinality  → hub {hub_id}")
            else:
                card_node_data = next(((nt, r) for nt, r in self.ontology.neighborhood_rules.items() if r["type"] == "max_degree"), (None, None))
                if card_node_data:
                    c_type, c_rule = card_node_data
                    card_rec = self.db.run_query(f"MATCH (c:{c_type}) RETURN c.id AS cid ORDER BY rand() LIMIT 1")
                    if card_rec:
                        cid = card_rec[0]["cid"]
                        overflow = c_rule["limit"] + config.CARDINALITY_OVERFLOW_OFFSET
                        self.db.run_query(f"MATCH (c:{c_type} {{id: '{cid}'}}), (h:{hub_type} {{id: '{hub_id}'}}) MERGE (c)-[:{c_rule['rel_type']}]->(h)")
                        self.db.run_query(f"""
                            MATCH (c:{c_type} {{id: '{cid}'}})
                            MATCH (b) WHERE c <> b
                            WITH c, collect(b)[0..{overflow}] AS chosen UNWIND chosen AS b
                            MERGE (c)-[:{c_rule['rel_type']}]->(b)
                        """)
                        queries.append(f"MATCH (c:{c_type} {{id: '{cid}'}})-[r:{c_rule['rel_type']}]->(n) WITH c, count(r) AS deg WHERE deg > {c_rule['limit']} MATCH (c)-[:{c_rule['rel_type']}]->(h:{hub_type} {{id: '{hub_id}'}}) RETURN c, deg, h")
                        print(f"  [V6 ✓] cardinality  → hub {hub_id} (external nodes)")

        with open("inconsistencies_overlap.txt", "w") as f:
            for q in queries:
                f.write(q + "\n")
        print("\nFinished injecting overlapping violations. Detection queries saved to inconsistencies_overlap.txt")

