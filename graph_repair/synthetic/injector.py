import random
import config

class ViolationInjector:
    def __init__(self, db, ontology):
        self.db = db
        self.ontology = ontology

    def inject_violations(self):
        print("Injecting violations...")

        violation_types = ["triple", "cardinality", "exclusive", "dependency", "comparison", "property_x"]
        total_success = 0

        with open("inconsistencies.txt", "w") as file:
            for v_type in violation_types:
                num_to_inject = random.randint(*config.INJECTION_COUNT_RANGE)
                inconsistency_query = ""
                injected_this_type = 0

                if v_type == "triple" and self.ontology.disallowed_patterns:
                    triple_src, triple_r, triple_tgt = random.choice(list(self.ontology.disallowed_patterns))
                    inconsistency_query = f"MATCH (n1:{triple_src})-[r:{triple_r}]->(n2:{triple_tgt}) RETURN n1, r, n2"
                    
                    result = self.db.run_query(f"""
                        MATCH (a:{triple_src}), (b:{triple_tgt}) 
                        WHERE a.id <> b.id AND NOT (a)-[:{triple_r}]->(b)
                        WITH a, b ORDER BY rand() LIMIT {num_to_inject}
                        MERGE (a)-[:{triple_r}]->(b)
                        RETURN count(a) AS count
                    """)
                    if result:
                        injected_this_type = result[0]["count"]

                elif v_type == "cardinality":
                    cands = [k for k, v in self.ontology.neighborhood_rules.items() if v["type"] == "max_degree"]
                    if cands:
                        card_node = random.choice(cands)
                        card_rule = self.ontology.neighborhood_rules[card_node]
                        inconsistency_query = f"MATCH (n1:{card_node})-[r:{card_rule['rel_type']}]->(n2) WITH n1, count(r) AS deg WHERE deg > {card_rule['limit']} RETURN n1"
                        overflow = card_rule["limit"] + config.CARDINALITY_OVERFLOW_OFFSET
                        
                        # Fetch multiple nodes to overflow
                        result = self.db.run_query(f"""
                            MATCH (a:{card_node})
                            WITH a ORDER BY rand() LIMIT {num_to_inject}
                            MATCH (b) WHERE a <> b AND NOT (a)-[:{card_rule['rel_type']}]->(b)
                            WITH a, collect(b)[0..{overflow}] AS chosen
                            UNWIND chosen AS b
                            MERGE (a)-[:{card_rule['rel_type']}]->(b)
                            RETURN count(DISTINCT a) AS count
                        """)
                        if result:
                            injected_this_type = result[0]["count"]

                elif v_type == "exclusive":
                    cands = [k for k, v in self.ontology.neighborhood_rules.items() if v["type"] == "exclusive"]
                    if cands:
                        excl_node = random.choice(cands)
                        excl_rule = self.ontology.neighborhood_rules[excl_node]
                        excl_p1, excl_p2 = excl_rule["conflict_pair"]
                        inconsistency_query = f"MATCH (n1:{excl_node})-[r1:{excl_rule['rel_type']}]->(n2:{excl_p1}), (n1)-[r2:{excl_rule['rel_type']}]->(n3:{excl_p2}) RETURN n1, r1, n2, r2, n3"
                        
                        result = self.db.run_query(f"""
                            MATCH (a:{excl_node})
                            WHERE NOT ((a)-[:{excl_rule['rel_type']}]->(:{excl_p1}) AND (a)-[:{excl_rule['rel_type']}]->(:{excl_p2}))
                            WITH a ORDER BY rand() LIMIT {num_to_inject}
                            MATCH (t1:{excl_p1}), (t2:{excl_p2})
                            WHERE t1 <> a AND t2 <> a AND t1 <> t2
                            WITH a, t1, t2 ORDER BY rand()
                            WITH a, collect({{t1:t1, t2:t2}})[0] AS pair
                            WHERE pair IS NOT NULL
                            WITH a, pair.t1 AS t1, pair.t2 AS t2
                            MERGE (a)-[:{excl_rule['rel_type']}]->(t1)
                            MERGE (a)-[:{excl_rule['rel_type']}]->(t2)
                            RETURN count(DISTINCT a) AS count
                        """)
                        if result:
                            injected_this_type = result[0]["count"]

                elif v_type == "dependency":
                    cands = [k for k, v in self.ontology.neighborhood_rules.items() if v["type"] == "dependency"]
                    if cands:
                        dep_node = random.choice(cands)
                        dep_rule = self.ontology.neighborhood_rules[dep_node]
                        inconsistency_query = (
                            f"MATCH (n1:{dep_node})-[r:{dep_rule['rel_type']}]->(n2:{dep_rule['trigger']}) "
                            f"WHERE NOT (n1)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']}) RETURN n1, r, n2"
                        )
                        
                        # Injects dependency violations by adding trigger and removing required
                        # Step 1: Add triggers
                        merge_result = self.db.run_query(f"""
                            MATCH (a:{dep_node})
                            WHERE NOT (a)-[:{dep_rule['rel_type']}]->(:{dep_rule['trigger']})
                               OR (a)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']})
                            WITH a ORDER BY rand() LIMIT {num_to_inject}
                            MATCH (b:{dep_rule['trigger']}) WHERE b.id <> a.id
                            WITH a, b ORDER BY rand()
                            WITH a, collect(b)[0] AS trigger_node
                            WHERE trigger_node IS NOT NULL
                            MERGE (a)-[:{dep_rule['rel_type']}]->(trigger_node)
                            RETURN collect(a.id) AS ids
                        """)
                        if merge_result and merge_result[0]["ids"]:
                            ids = merge_result[0]["ids"]
                            # Step 2: Delete required relationships for these nodes
                            self.db.run_query(f"""
                                UNWIND $ids AS sid
                                MATCH (a:{dep_node} {{id: sid}})-[r:{dep_rule['rel_type']}]->(c:{dep_rule['required']})
                                DELETE r
                            """, params={"ids": ids})
                            injected_this_type = len(ids)

                elif v_type == "comparison":
                    comp_rule_node = None
                    comp_rule = None
                    for nt, rule in self.ontology.neighborhood_rules.items():
                        if rule["type"] == "comparison":
                            comp_rule_node = nt
                            comp_rule = rule
                            break

                    if comp_rule:
                        inconsistency_query = f"MATCH (a)-[r {{A1: 'active'}}]->(b) WHERE a.prop <= b.prop RETURN a, r, b"
                        # Step 1: Create active relationships
                        self.db.run_query(f"""
                            MATCH (a:{comp_rule_node}), (b:{comp_rule['target']})
                            WHERE a.id <> b.id AND a.prop IS NOT NULL AND b.prop IS NOT NULL
                            WITH a, b ORDER BY rand() LIMIT {num_to_inject}
                            MERGE (a)-[:{comp_rule['rel_type']} {{A1: 'active'}}]->(b)
                            SET a.prop = b.prop + {config.COMPARISON_INCREMENT}
                        """)
                        # Step 2: Invert property for violation
                        result = self.db.run_query(f"""
                            MATCH (a)-[r {{A1: 'active'}}]->(b)
                            WHERE a.prop > b.prop
                            WITH a, b ORDER BY rand() LIMIT {num_to_inject}
                            SET a.prop = b.prop - {config.COMPARISON_VIOLATION_OFFSET}
                            RETURN count(a) AS count
                        """)
                        if result:
                            injected_this_type = result[0]["count"]

                elif v_type == "property_x" and self.ontology.property_constraint:
                    constraint = self.ontology.property_constraint
                    target_type = constraint["node_type"]
                    threshold = constraint["threshold"]
                    op = constraint.get("operator", ">")
                    
                    if op == ">":
                        inconsistency_query = f"MATCH (n:{target_type}) WHERE n.x <= {threshold} RETURN n"
                        result = self.db.run_query(f"""
                            MATCH (n:{target_type}) WHERE n.x > {threshold}
                            WITH n ORDER BY rand() LIMIT {num_to_inject}
                            SET n.x = {threshold} - {config.PROPERTY_VIOLATION_OFFSET}
                            RETURN count(n) AS count
                        """)
                    else: # op == "<"
                        inconsistency_query = f"MATCH (n:{target_type}) WHERE n.x >= {threshold} RETURN n"
                        result = self.db.run_query(f"""
                            MATCH (n:{target_type}) WHERE n.x < {threshold}
                            WITH n ORDER BY rand() LIMIT {num_to_inject}
                            SET n.x = {threshold} + {config.PROPERTY_VIOLATION_OFFSET}
                            RETURN count(n) AS count
                        """)
                    if result:
                        injected_this_type = result[0]["count"]

                if injected_this_type > 0:
                    print(f"  [Success] Injected {injected_this_type} {v_type} violation(s).")
                    file.write(f"{inconsistency_query}\n")
                    total_success += injected_this_type
                else:
                    print(f"  [Failed] Could not inject {v_type} violation (graph preconditions not met).")

        print(f"Finished. Total violations injected: {total_success}")

