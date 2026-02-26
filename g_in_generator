import random
import json
from neo4j import GraphDatabase

class Generator:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.num_node_types = 5  
        self.num_rel_types = 4   
        
        #rules
        self.allowed_patterns = set()
        self.disallowed_patterns = set()
        self.neighborhood_rules = {} 

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    # laws
    def generate_rules(self, num_allowed=20, num_disallowed=5):
        
        #triples
        all_node_types = [f"N{i}" for i in range(1, self.num_node_types + 1)]
        all_rel_types = [f"R{i}" for i in range(1, self.num_rel_types + 1)]
        
        universe = set()                # universe has nodes*nodes*rels patterns
        for src in all_node_types:
            for tgt in all_node_types:
                for rel in all_rel_types:
                    universe.add((src, rel, tgt))
        
        self.allowed_patterns = set(random.sample(list(universe), num_allowed))
        remaining = universe - self.allowed_patterns
        self.disallowed_patterns = set(random.sample(list(remaining), num_disallowed))

        # neighborhood constratins
        for n_type in all_node_types:
            rand_val = random.random()
            
            # outgoing edges
            if rand_val < 0.2:
                self.neighborhood_rules[n_type] = {
                    "type": "max_degree",
                    "limit": random.randint(1, 5),
                    "rel_type": random.choice(all_rel_types)
                }
            
            # exclusive (if A->B then A!->C)
            elif rand_val < 0.65:
                others = [t for t in all_node_types if t != n_type]
                if len(others) >= 2:
                    self.neighborhood_rules[n_type] = {
                        "type": "exclusive",
                        "conflict_pair": random.sample(others, 2), 
                        "rel_type": random.choice(all_rel_types)
                    }

            # and
            elif rand_val < 0.9:
                others = [t for t in all_node_types if t != n_type]
                if len(others) >= 2:
                    pair = random.sample(others, 2)
                    self.neighborhood_rules[n_type] = {
                        "type": "dependency",
                        "trigger": pair[0],   
                        "required": pair[1],  
                        "rel_type": random.choice(all_rel_types)
                    }
            else:
                others = [t for t in all_node_types if t != n_type]
                if others:
                    target = random.choice(others)
                    self.neighborhood_rules[n_type] = {
                        "type": "temporal",
                        "target": target,
                        "rel_type": random.choice(all_rel_types) # The specific relation for the date rule
                    }

    # clean graph
    def generate_valid_graph(self, num_nodes=80):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print(f"creating nodes")
            
            # nodes
            node_ids = []
            for i in range(num_nodes):
                n_type = f"N{random.randint(1, self.num_node_types)}"
                uid = f"node_{i}"
                session.run(f"CREATE (n:{n_type} {{id: '{uid}'}})")
                node_ids.append((uid, n_type))

            
            global_neighbors = {uid: set() for uid, _ in node_ids}

            # Edges
            print(" now edges")
            for src_id, src_type in node_ids:
                
                # current source node rules
                max_degree_limit = 999
                exclusive_forbidden = set()
                exclusive_rule = None
                dependency_rule = None 
                
                if src_type in self.neighborhood_rules:
                    rule = self.neighborhood_rules[src_type]
                    if rule["type"] == "max_degree":
                        max_degree_limit = rule["limit"]
                    elif rule["type"] == "exclusive":
                        exclusive_rule = rule
                    elif rule["type"] == "dependency":
                        dependency_rule = rule

                connections_made = 0
                random.shuffle(node_ids)
                
                for tgt_id, tgt_type in node_ids:
                    if src_id == tgt_id: continue
                    if connections_made >= max_degree_limit: break
                    
                    #  source constraints
                    if tgt_type in exclusive_forbidden: continue

                    # target constraints
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
                    
                    possible_rels = [r for (s, r, t) in self.allowed_patterns 
                                     if s == src_type and t == tgt_type]
                    
                    if possible_rels and random.random() < 0.2:
                        r_type = random.choice(possible_rels)
                        
                        
                        session.run(f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            MERGE (a)-[:{r_type}]->(b)
                        """)
                        connections_made += 1

                        
                        global_neighbors[src_id].add(tgt_type)
                        global_neighbors[tgt_id].add(src_type)

                        
                        if exclusive_rule and tgt_type in exclusive_rule["conflict_pair"]:
                            pair = exclusive_rule["conflict_pair"]
                            other = pair[1] if tgt_type == pair[0] else pair[0]
                            exclusive_forbidden.add(other)

                        
                        if dependency_rule and tgt_type == dependency_rule["trigger"]:
                            req_type = dependency_rule["required"]
                            req_rel = dependency_rule["rel_type"]
                            
                            
                            session.run(f"""
                                MATCH (src {{id: '{src_id}'}})
                                MATCH (partner:{req_type}) WHERE partner.id <> src.id
                                WITH src, partner LIMIT 1
                                MERGE (src)-[:{req_rel}]->(partner)
                            """)
                            
                            
                            global_neighbors[src_id].add(req_type)
                           

    
    #incon
    def inject_violations(self, count=5):
        print(f"Injecting {count} violations...")
        
        with self.driver.session() as session:
            success_count = 0
            max_retries = count * 3  
            attempts = 0

            while success_count < count and attempts < max_retries:
                attempts += 1
                violation_type = random.choice(["triple", "cardinality", "exclusive", "dependency"])
                result = None  

                # FORBIDDEN TRIPLE
                if violation_type == "triple" and self.disallowed_patterns:
                    src, r, tgt = random.choice(list(self.disallowed_patterns))
                    result = session.run(f"""
                        MATCH (a:{src}), (b:{tgt}) 
                        WHERE a.id <> b.id 
                        WITH a,b LIMIT 1 
                        MERGE (a)-[:{r}]->(b) 
                        SET a.inconsistency='forbidden_triple'
                    """)

                # CARDINALITY
                elif violation_type == "cardinality":
                    cands = [k for k, v in self.neighborhood_rules.items() if v["type"] == "max_degree"]
                    if cands:
                        v = random.choice(cands)
                        rule = self.neighborhood_rules[v]
                        overflow = rule["limit"] + 2
                        rel_type = rule["rel_type"]

                        result = session.run(f"""
                             MATCH (a:{v})
                             WITH a LIMIT 1
                             MATCH (b)
                             WHERE a <> b AND NOT (a)-[:{rel_type}]->(b)
                             WITH a, collect(b) as candidates
                             WITH a, candidates[0..{overflow}] as chosen
                             UNWIND chosen AS b
                             MERGE (a)-[:{rel_type}]->(b)
                             SET a.inconsistency = 'cardinality'
                        """)

                # EXCLUSIVE 
                elif violation_type == "exclusive":
                    cands = [k for k,v in self.neighborhood_rules.items() if v["type"]=="exclusive"]
                    if cands:
                        v = random.choice(cands)
                        rule = self.neighborhood_rules[v]
                        p1, p2 = rule["conflict_pair"]
                        result = session.run(f"""
                            MATCH (a:{v}) WITH a LIMIT 1 
                            MATCH (t1:{p1}), (t2:{p2}) 
                            WITH a,t1,t2 LIMIT 1 
                            MERGE (a)-[:{rule['rel_type']}]->(t1) 
                            MERGE (a)-[:{rule['rel_type']}]->(t2) 
                            SET a.inconsistency='exclusive_violation'
                        """)

                # DEPENDENCY 
                elif violation_type == "dependency":
                    cands = [k for k,v in self.neighborhood_rules.items() if v["type"]=="dependency"]
                    if cands:
                        v_type = random.choice(cands)
                        rule = self.neighborhood_rules[v_type]
                        trigger = rule["trigger"]
                        required = rule["required"]
                        rel = rule["rel_type"]
                        
                        result = session.run(f"""
                            MATCH (a:{v_type}), (b:{trigger}) 
                            WHERE a.id <> b.id 
                            WITH a, b LIMIT 1
                            MERGE (a)-[:{rel}]->(b)
                            WITH a
                            OPTIONAL MATCH (a)-[r]->(c:{required})
                            DELETE r
                            SET a.inconsistency = 'missing_dependency'
                        """)

                
                if result:
                    summary = result.consume()
                    if summary.counters.properties_set > 0:
                        print(f"  [Success] Injected {violation_type} violation.")
                        success_count += 1
                    else:
                        
                        pass
            
            if success_count < count:
                print(f"Warning: Only managed to inject {success_count}/{count} violations.")
            else:
                print(f"Successfully injected {success_count} violations.")

    # json
    def export_ontology(self, filename="ontology_final.json"):
        data = {
            "triples": {
                "allowed": [list(p) for p in self.allowed_patterns],
                "disallowed": [list(p) for p in self.disallowed_patterns]
            },
            "neighborhood_constraints": self.neighborhood_rules
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        


if __name__ == "__main__":
    gen = Generator("neo4j+s://9738bd7b.databases.neo4j.io", ("neo4j", "JMOdIBduJdKFNl560eV6CTVWlpYE0iklAstPv7DuDjs"))
    gen.clear_database()
    gen.generate_rules(num_allowed=20, num_disallowed=5)
    gen.generate_valid_graph(num_nodes=50)
    gen.export_ontology()
    #gen.inject_violations(count=5)
    gen.close()
