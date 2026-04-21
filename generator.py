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

    # clean graph
    def generate_valid_graph(self, num_nodes=80):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print(f"created nodes")
            
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
    gen = Generator("neo4j+s://5f7f0ba1.databases.neo4j.io", ("neo4j", "Sy4p5y6EEKeKQPmbFS7S1kLe4ggqo7rZDFA0WSTSW2o"))
    gen.clear_database()
    gen.generate_rules(num_allowed=20, num_disallowed=5)
    gen.generate_valid_graph(num_nodes=50)
    gen.export_ontology()
    gen.close()