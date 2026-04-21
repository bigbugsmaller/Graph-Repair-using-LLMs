import random
import json
from neo4j import GraphDatabase
from datetime import date, timedelta

# =============================================================================
#  DESIGN: HUB-ANCHORED OVERLAPPING VIOLATIONS
#
#  Core idea: pick ONE hub node H, then inject violations such that
#  every detection query returns H in its result set.
#
#  H appears as:
#    property_x  → H.x below threshold              (H is the bad node)
#    exclusive   → H connects to both conflict pair  (H breaks its own rule)
#    triple      → H is source of disallowed edge    (H is the bad source)
#    temporal    → corrupted edge points INTO H      (H appears as target)
#    dependency  → another node connects to H as     (H appears as trigger)
#                  its trigger but loses required
#    cardinality → card_node overflows AND has edge  (H appears joined through edge)
#                  to H, so H is in the query result
#
#  This guarantees: run any of the 6 detection queries → H appears every time.
# =============================================================================

class OverlapGenerator:

    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.num_node_types = 5
        self.num_rel_types  = 4
        self.allowed_patterns    = set()
        self.disallowed_patterns = set()
        self.neighborhood_rules  = {}
        self.property_constraint = None

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    # =========================================================================
    # 1. GENERATE RULES
    # =========================================================================
    def generate_rules(self, num_allowed=20, num_disallowed=5):
        all_node_types = [f"N{i}" for i in range(1, self.num_node_types + 1)]
        all_rel_types  = [f"R{i}" for i in range(1, self.num_rel_types  + 1)]

        universe = {(s, r, t) for s in all_node_types
                               for t in all_node_types
                               for r in all_rel_types}
        self.allowed_patterns    = set(random.sample(list(universe), num_allowed))
        remaining                = universe - self.allowed_patterns
        self.disallowed_patterns = set(random.sample(list(remaining), num_disallowed))

        active_types = {s for (s, _, t) in self.allowed_patterns} | \
                       {t for (_, _, t) in self.allowed_patterns}
        if active_types:
            self.property_constraint = {
                "node_type": random.choice(list(active_types)),
                "threshold": random.randint(30, 70)
            }

        for n_type in all_node_types:
            rv     = random.random()
            others = [t for t in all_node_types if t != n_type]
            if rv < 0.2:
                self.neighborhood_rules[n_type] = {
                    "type": "max_degree", "limit": random.randint(1, 5),
                    "rel_type": random.choice(all_rel_types)
                }
            elif rv < 0.5 and len(others) >= 2:
                self.neighborhood_rules[n_type] = {
                    "type": "exclusive",
                    "conflict_pair": random.sample(others, 2),
                    "rel_type": random.choice(all_rel_types)
                }
            elif rv < 0.75 and len(others) >= 2:
                pair = random.sample(others, 2)
                self.neighborhood_rules[n_type] = {
                    "type": "dependency",
                    "trigger": pair[0], "required": pair[1],
                    "rel_type": random.choice(all_rel_types)
                }
            elif others:
                self.neighborhood_rules[n_type] = {
                    "type": "temporal",
                    "target": random.choice(others),
                    "rel_type": random.choice(all_rel_types)
                }

        def _ensure(rule_type, builder):
            if not any(v["type"] == rule_type for v in self.neighborhood_rules.values()):
                unassigned = [t for t in all_node_types if t not in self.neighborhood_rules]
                ft = random.choice(unassigned if unassigned else all_node_types)
                self.neighborhood_rules[ft] = builder(ft, all_node_types, all_rel_types)
                print(f"  [Guaranteed] {rule_type} → {ft}")

        _ensure("max_degree", lambda ft, nt, rt: {
            "type": "max_degree", "limit": random.randint(1, 5),
            "rel_type": random.choice(rt)
        })
        _ensure("exclusive", lambda ft, nt, rt: {
            "type": "exclusive",
            "conflict_pair": random.sample([t for t in nt if t != ft], 2),
            "rel_type": random.choice(rt)
        })
        _ensure("dependency", lambda ft, nt, rt: {
            "type": "dependency",
            "trigger":  (p := random.sample([t for t in nt if t != ft], 2))[0],
            "required": p[1],
            "rel_type": random.choice(rt)
        })
        _ensure("temporal", lambda ft, nt, rt: {
            "type": "temporal",
            "target": random.choice([t for t in nt if t != ft]),
            "rel_type": random.choice(rt)
        })

    # =========================================================================
    # 2. GENERATE VALID GRAPH
    # =========================================================================
    def generate_valid_graph(self, num_nodes=80):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Creating nodes...")

            needs_date   = set()
            needs_prop_x = set()
            for src_type, rule in self.neighborhood_rules.items():
                if rule["type"] == "temporal":
                    needs_date.add(src_type)
                    needs_date.add(rule["target"])
            if self.property_constraint:
                needs_prop_x.add(self.property_constraint["node_type"])

            node_ids = []
            for i in range(num_nodes):
                n_type = f"N{random.randint(1, self.num_node_types)}"
                uid    = f"node_{i}"
                props  = [f"id: '{uid}'"]
                if n_type in needs_date:
                    start_dt = date(2000, 1, 1)
                    delta    = (date(2023, 12, 31) - start_dt).days
                    rd       = start_dt + timedelta(days=random.randint(0, delta))
                    props.append(f"date_val: date('{rd.strftime('%Y-%m-%d')}')")
                if n_type in needs_prop_x:
                    limit = self.property_constraint["threshold"]
                    props.append(f"x: {random.randint(limit + 1, 100)}")
                session.run(f"CREATE (n:{n_type} {{ {', '.join(props)} }})")
                node_ids.append((uid, n_type))

            print("Connecting nodes (clean, rule-compliant)...")
            global_neighbors = {uid: set() for uid, _ in node_ids}
            for src_id, src_type in list(node_ids):
                max_degree_limit = 999
                exclusive_rule = dependency_rule = temporal_rule = None
                exclusive_forbidden = set()

                if src_type in self.neighborhood_rules:
                    rule = self.neighborhood_rules[src_type]
                    if   rule["type"] == "max_degree":  max_degree_limit = rule["limit"]
                    elif rule["type"] == "exclusive":    exclusive_rule   = rule
                    elif rule["type"] == "dependency":   dependency_rule  = rule
                    elif rule["type"] == "temporal":     temporal_rule    = rule

                connections_made = 0
                inner = list(node_ids)
                random.shuffle(inner)

                for tgt_id, tgt_type in inner:
                    if src_id == tgt_id: continue
                    if connections_made >= max_degree_limit: break
                    if tgt_type in exclusive_forbidden: continue
                    if tgt_type in self.neighborhood_rules:
                        tr = self.neighborhood_rules[tgt_type]
                        if tr["type"] == "exclusive":
                            pair = tr["conflict_pair"]
                            if src_type in pair:
                                enemy = pair[1] if src_type == pair[0] else pair[0]
                                if enemy in global_neighbors[tgt_id]: continue

                    possible_rels = [r for (s, r, t) in self.allowed_patterns
                                     if s == src_type and t == tgt_type]
                    if not possible_rels or random.random() >= 0.2: continue
                    r_type = random.choice(possible_rels)

                    if (temporal_rule and tgt_type == temporal_rule["target"]
                            and r_type == temporal_rule["rel_type"]):
                        session.run(f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            WHERE a.date_val <= b.date_val
                            SET a.date_val = b.date_val + duration('P1D')
                        """)
                        session.run(f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            MERGE (a)-[:{r_type} {{A1: 'active'}}]->(b)
                        """)
                    else:
                        session.run(f"""
                            MATCH (a {{id: '{src_id}'}}), (b {{id: '{tgt_id}'}})
                            MERGE (a)-[:{r_type}]->(b)
                        """)

                    connections_made += 1
                    global_neighbors[src_id].add(tgt_type)
                    global_neighbors[tgt_id].add(src_type)

                    if exclusive_rule and tgt_type in exclusive_rule["conflict_pair"]:
                        pair  = exclusive_rule["conflict_pair"]
                        other = pair[1] if tgt_type == pair[0] else pair[0]
                        exclusive_forbidden.add(other)

                    if dependency_rule and tgt_type == dependency_rule["trigger"]:
                        session.run(f"""
                            MATCH (src {{id: '{src_id}'}})
                            MATCH (partner:{dependency_rule['required']})
                            WHERE partner.id <> src.id
                            WITH src, partner LIMIT 1
                            MERGE (src)-[:{dependency_rule['rel_type']}]->(partner)
                        """)
                        global_neighbors[src_id].add(dependency_rule["required"])

    # =========================================================================
    # 3. SCORE EACH NODE TYPE FOR HUB POTENTIAL
    #
    #  A type scores points for every violation whose detection query
    #  will return H when H is chosen as hub:
    #
    #   +3  owns property constraint  → H.x query returns H directly
    #   +3  owns exclusive rule       → exclusive query returns H directly
    #   +3  is temporal TARGET        → temporal query returns H as target
    #   +3  is dependency TRIGGER     → dependency query returns H as trigger
    #   +2  owns temporal rule        → temporal query returns H as source
    #   +2  owns dependency rule      → dependency query returns H as source
    #   +2  owns max_degree rule      → cardinality query returns H directly
    #   +1  appears in disallowed as src or tgt → triple query returns H
    # =========================================================================
    def _score_hub_types(self):
        all_node_types = [f"N{i}" for i in range(1, self.num_node_types + 1)]
        scores = {nt: 0 for nt in all_node_types}

        for nt, rule in self.neighborhood_rules.items():
            if rule["type"] == "max_degree":
                scores[nt] += 2
            elif rule["type"] == "exclusive":
                scores[nt] += 3
            elif rule["type"] == "dependency":
                scores[nt] += 2
                scores[rule["trigger"]]  += 3   # trigger appears in dep query
                scores[rule["required"]] += 0
            elif rule["type"] == "temporal":
                scores[nt] += 2
                scores[rule["target"]] += 3     # target appears in temporal query

        if self.property_constraint:
            scores[self.property_constraint["node_type"]] += 3

        for (s, _, t) in self.disallowed_patterns:
            scores[s] += 1
            scores[t] += 1

        return scores

    # =========================================================================
    # 4. INJECT — ALL VIOLATIONS ANCHORED TO ONE HUB NODE H
    #
    #  Every detection query written here includes hub_id in its result.
    #  Run any query → H appears. That is true, verifiable overlap.
    # =========================================================================
    def inject_overlapping_violations(self):
        print("\nInjecting hub-anchored overlapping violations...")
        injected = []
        queries  = []

        with self.driver.session() as session:

            # ── Pick hub ──────────────────────────────────────────────────────
            scores   = self._score_hub_types()
            hub_type = max(scores, key=scores.get)
            print(f"  Scores : {scores}")
            print(f"  Hub type selected: {hub_type} (score={scores[hub_type]})")

            rec = session.run(
                f"MATCH (h:{hub_type}) RETURN h.id AS nid ORDER BY rand() LIMIT 1"
            ).single()
            if not rec:
                print(f"  ❌ No {hub_type} node in graph"); return []
            hub_id   = rec["nid"]
            hub_rule = self.neighborhood_rules.get(hub_type)
            print(f"  Hub node: {hub_id}\n")

            # ── V1: property_x ────────────────────────────────────────────────
            # H.x set below threshold → detection query returns H directly
            if self.property_constraint and \
               self.property_constraint["node_type"] == hub_type:
                thr = self.property_constraint["threshold"]
                r = session.run(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}})
                    WHERE h.x > {thr}
                    SET h.x = {thr} - 10
                    RETURN h
                """)
                if r.peek():
                    print(f"  [V1 ✓] property_x   → hub {hub_id}.x = {thr-10} (threshold {thr})")
                    injected.append("property_x")
                    queries.append(
                        f"MATCH (h:{hub_type} {{id: '{hub_id}'}}) "
                        f"WHERE h.x <= {thr} RETURN h"
                    )
                else:
                    print(f"  [V1 –] property_x   → hub has no x property")
            else:
                print(f"  [V1 –] property_x   → {hub_type} does not own constraint")

            # ── V2: exclusive ─────────────────────────────────────────────────
            # H connects to BOTH conflict partners → query returns H as source
            if hub_rule and hub_rule["type"] == "exclusive":
                p1, p2 = hub_rule["conflict_pair"]
                r = session.run(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}})
                    MATCH (t1:{p1}), (t2:{p2})
                    WHERE t1.id <> h.id AND t2.id <> h.id AND t1.id <> t2.id
                    WITH h, t1, t2 LIMIT 1
                    MERGE (h)-[:{hub_rule['rel_type']}]->(t1)
                    MERGE (h)-[:{hub_rule['rel_type']}]->(t2)
                    RETURN h
                """)
                if r.peek():
                    print(f"  [V2 ✓] exclusive    → hub {hub_id} → {p1} AND {p2}")
                    injected.append("exclusive")
                    queries.append(
                        f"MATCH (h:{hub_type} {{id: '{hub_id}'}})"
                        f"-[r1:{hub_rule['rel_type']}]->(n2:{p1}), "
                        f"(h)-[r2:{hub_rule['rel_type']}]->(n3:{p2}) "
                        f"RETURN h, r1, n2, r2, n3"
                    )
                else:
                    print(f"  [V2 –] exclusive    → conflict partner types not found")
            else:
                print(f"  [V2 –] exclusive    → {hub_type} rule is '{hub_rule['type'] if hub_rule else 'none'}'")

            # ── V3: triple ────────────────────────────────────────────────────
            # Prefer H as SOURCE of disallowed edge → query returns H as src
            # Fallback: H as TARGET → query returns H as tgt
            hub_src = [(s, r, t) for (s, r, t) in self.disallowed_patterns if s == hub_type]
            hub_tgt = [(s, r, t) for (s, r, t) in self.disallowed_patterns if t == hub_type]
            triple_done = False

            for (s, rel, t) in hub_src:
                r = session.run(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}}), (tgt:{t})
                    WHERE h.id <> tgt.id WITH h, tgt LIMIT 1
                    MERGE (h)-[:{rel}]->(tgt) RETURN h
                """)
                if r.peek():
                    print(f"  [V3 ✓] triple       → hub {hub_id} src of disallowed ({s})-[{rel}]->({t})")
                    injected.append("triple")
                    queries.append(
                        f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r:{rel}]->(tgt:{t}) "
                        f"RETURN h, r, tgt"
                    )
                    triple_done = True; break

            if not triple_done:
                for (s, rel, t) in hub_tgt:
                    r = session.run(f"""
                        MATCH (src:{s}), (h:{hub_type} {{id: '{hub_id}'}})
                        WHERE src.id <> h.id WITH src, h LIMIT 1
                        MERGE (src)-[:{rel}]->(h) RETURN h
                    """)
                    if r.peek():
                        print(f"  [V3 ✓] triple       → hub {hub_id} tgt of disallowed ({s})-[{rel}]->({t})")
                        injected.append("triple")
                        queries.append(
                            f"MATCH (src:{s})-[r:{rel}]->(h:{hub_type} {{id: '{hub_id}'}}) "
                            f"RETURN src, r, h"
                        )
                        triple_done = True; break

            if not triple_done:
                print(f"  [V3 –] triple       → {hub_type} not in any disallowed pattern")

            # ── V4: temporal ──────────────────────────────────────────────────
            # Case A: another type's temporal rule TARGETS hub_type
            #         → corrupt edge coming INTO H; query returns H as target
            # Case B: hub owns temporal rule
            #         → corrupt edge going OUT of H; query returns H as source
            temp_src_type, temp_rule = next(
                ((nt, r) for nt, r in self.neighborhood_rules.items()
                 if r["type"] == "temporal" and r["target"] == hub_type),
                (None, None)
            )
            if temp_rule is None and hub_rule and hub_rule["type"] == "temporal":
                temp_src_type = hub_type
                temp_rule     = hub_rule

            if temp_rule:
                if temp_src_type != hub_type:   # H is the TEMPORAL TARGET
                    session.run(f"""
                        MATCH (src:{temp_src_type}), (h:{hub_type} {{id: '{hub_id}'}})
                        WHERE src.id <> h.id
                          AND src.date_val IS NOT NULL AND h.date_val IS NOT NULL
                        WITH src, h LIMIT 1
                        MERGE (src)-[:{temp_rule['rel_type']} {{A1: 'active'}}]->(h)
                        SET src.date_val = h.date_val + duration('P1D')
                    """)
                    r = session.run(f"""
                        MATCH (src:{temp_src_type})
                              -[rr {{A1: 'active'}}]->(h:{hub_type} {{id: '{hub_id}'}})
                        WHERE src.date_val > h.date_val
                        WITH src, h LIMIT 1
                        SET src.date_val = h.date_val - duration('P10D')
                        RETURN h
                    """)
                    if r.peek():
                        print(f"  [V4 ✓] temporal     → hub {hub_id} is temporal TARGET, src date corrupted")
                        injected.append("temporal")
                        queries.append(
                            f"MATCH (src:{temp_src_type})-[r {{A1: 'active'}}]"
                            f"->(h:{hub_type} {{id: '{hub_id}'}}) "
                            f"WHERE src.date_val <= h.date_val RETURN src, r, h"
                        )
                    else:
                        print(f"  [V4 –] temporal     → no valid temporal edge found to hub")

                else:                           # H is the TEMPORAL SOURCE
                    session.run(f"""
                        MATCH (h:{hub_type} {{id: '{hub_id}'}}), (tgt:{temp_rule['target']})
                        WHERE h.id <> tgt.id
                          AND h.date_val IS NOT NULL AND tgt.date_val IS NOT NULL
                        WITH h, tgt LIMIT 1
                        MERGE (h)-[:{temp_rule['rel_type']} {{A1: 'active'}}]->(tgt)
                        SET h.date_val = tgt.date_val + duration('P1D')
                    """)
                    r = session.run(f"""
                        MATCH (h:{hub_type} {{id: '{hub_id}'}})-[rr {{A1: 'active'}}]
                              ->(tgt:{temp_rule['target']})
                        WHERE h.date_val > tgt.date_val WITH h, tgt LIMIT 1
                        SET h.date_val = tgt.date_val - duration('P10D')
                        RETURN h
                    """)
                    if r.peek():
                        print(f"  [V4 ✓] temporal     → hub {hub_id} is temporal SOURCE, date corrupted")
                        injected.append("temporal")
                        queries.append(
                            f"MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r {{A1: 'active'}}]"
                            f"->(tgt:{temp_rule['target']}) "
                            f"WHERE h.date_val <= tgt.date_val RETURN h, r, tgt"
                        )
                    else:
                        print(f"  [V4 –] temporal     → no valid temporal edge found from hub")
            else:
                print(f"  [V4 –] temporal     → {hub_type} not in any temporal rule")

            # ── V5: dependency ────────────────────────────────────────────────
            # Case A: hub_type is someone else's dependency TRIGGER
            #         → dep_src connects to H as trigger, loses required
            #         → query: MATCH (dep_src)-[:R]->(h) WHERE NOT (dep_src)->(:req) RETURN dep_src, h
            #         → H appears in result as trigger
            # Case B: hub owns dependency rule
            #         → H connects to trigger, loses its required edge
            #         → query: MATCH (h)-[:R]->(trig) WHERE NOT (h)->(:req) RETURN h
            dep_src_type, dep_rule = next(
                ((nt, r) for nt, r in self.neighborhood_rules.items()
                 if r["type"] == "dependency" and r["trigger"] == hub_type),
                (None, None)
            )
            if dep_rule is None and hub_rule and hub_rule["type"] == "dependency":
                dep_src_type = hub_type
                dep_rule     = hub_rule

            if dep_rule:
                if dep_src_type != hub_type:    # H is the TRIGGER
                    dep_rec = session.run(f"""
                        MATCH (dep:{dep_src_type}), (h:{hub_type} {{id: '{hub_id}'}})
                        WHERE dep.id <> h.id
                          AND NOT (dep)-[:{dep_rule['rel_type']}]->(h)
                        RETURN dep.id AS did LIMIT 1
                    """).single()
                    if dep_rec:
                        dep_id = dep_rec["did"]
                        session.run(f"""
                            MATCH (dep:{dep_src_type} {{id: '{dep_id}'}}),
                                  (h:{hub_type} {{id: '{hub_id}'}})
                            MERGE (dep)-[:{dep_rule['rel_type']}]->(h)
                        """)
                        session.run(f"""
                            MATCH (dep:{dep_src_type} {{id: '{dep_id}'}})-[r]
                                  ->(req:{dep_rule['required']})
                            DELETE r
                        """)
                        r = session.run(f"MATCH (h:{hub_type} {{id: '{hub_id}'}}) RETURN h")
                        if r.peek():
                            print(f"  [V5 ✓] dependency   → {dep_id}({dep_src_type}) connects to hub {hub_id} as trigger, required deleted")
                            injected.append("dependency")
                            queries.append(
                                f"MATCH (dep:{dep_src_type})-[r:{dep_rule['rel_type']}]"
                                f"->(h:{hub_type} {{id: '{hub_id}'}}) "
                                f"WHERE NOT (dep)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']}) "
                                f"RETURN dep, r, h"
                            )
                    else:
                        print(f"  [V5 –] dependency   → no dep_src node found to connect to hub")

                else:                           # H is the DEP SOURCE
                    trig_rec = session.run(f"""
                        MATCH (h:{hub_type} {{id: '{hub_id}'}}), (trig:{dep_rule['trigger']})
                        WHERE h.id <> trig.id
                          AND NOT (h)-[:{dep_rule['rel_type']}]->(trig)
                        RETURN trig.id AS tid LIMIT 1
                    """).single()
                    if trig_rec:
                        session.run(f"""
                            MATCH (h:{hub_type} {{id: '{hub_id}'}}),
                                  (trig:{dep_rule['trigger']} {{id: '{trig_rec["tid"]}'}})
                            MERGE (h)-[:{dep_rule['rel_type']}]->(trig)
                        """)
                        session.run(f"""
                            MATCH (h:{hub_type} {{id: '{hub_id}'}})-[r]
                                  ->(req:{dep_rule['required']})
                            DELETE r
                        """)
                        r = session.run(f"MATCH (h:{hub_type} {{id: '{hub_id}'}}) RETURN h")
                        if r.peek():
                            print(f"  [V5 ✓] dependency   → hub {hub_id} connects to trigger, required deleted")
                            injected.append("dependency")
                            queries.append(
                                f"MATCH (h:{hub_type} {{id: '{hub_id}'}})"
                                f"-[r:{dep_rule['rel_type']}]->(trig:{dep_rule['trigger']}) "
                                f"WHERE NOT (h)-[:{dep_rule['rel_type']}]->(:{dep_rule['required']}) "
                                f"RETURN h, r, trig"
                            )
                    else:
                        print(f"  [V5 –] dependency   → no trigger node found for hub")
            else:
                print(f"  [V5 –] dependency   → {hub_type} not in any dependency rule")

            # ── V6: cardinality ───────────────────────────────────────────────
            # Case A: hub owns max_degree → overflow H directly
            #         → query: MATCH (h:Th {id:H})-[r:R]->() WITH h, count(r) AS deg WHERE deg > limit RETURN h
            # Case B: hub doesn't own max_degree → find a card_node, overflow it,
            #         FORCE one edge from card_node TO H so H appears in query
            #         → query: MATCH (c:Tc)-[:R]->(h:Th {id:H}) WITH c, count{(c)-[:R]->()} AS deg WHERE deg > limit RETURN c, h
            if hub_rule and hub_rule["type"] == "max_degree":
                overflow = hub_rule["limit"] + 2
                r = session.run(f"""
                    MATCH (h:{hub_type} {{id: '{hub_id}'}})
                    MATCH (b) WHERE h <> b
                    WITH h, collect(b)[0..{overflow}] AS chosen UNWIND chosen AS b
                    MERGE (h)-[:{hub_rule['rel_type']}]->(b)
                    RETURN h
                """)
                if r.peek():
                    print(f"  [V6 ✓] cardinality  → hub {hub_id} overflowed ({overflow} edges, limit={hub_rule['limit']})")
                    injected.append("cardinality")
                    queries.append(
                        f"MATCH (h:{hub_type} {{id: '{hub_id}'}})"
                        f"-[r:{hub_rule['rel_type']}]->(n) "
                        f"WITH h, count(r) AS deg "
                        f"WHERE deg > {hub_rule['limit']} RETURN h"
                    )
            else:
                card_type, card_rule = next(
                    ((nt, r) for nt, r in self.neighborhood_rules.items()
                     if r["type"] == "max_degree"),
                    (None, None)
                )
                if card_type:
                    card_rec = session.run(
                        f"MATCH (c:{card_type}) RETURN c.id AS cid ORDER BY rand() LIMIT 1"
                    ).single()
                    if card_rec:
                        card_id  = card_rec["cid"]
                        overflow = card_rule["limit"] + 2
                        # Force one edge from card_node TO hub so hub appears in query
                        session.run(f"""
                            MATCH (c:{card_type} {{id: '{card_id}'}}),
                                  (h:{hub_type} {{id: '{hub_id}'}})
                            MERGE (c)-[:{card_rule['rel_type']}]->(h)
                        """)
                        # Fill remaining edges to overflow
                        session.run(f"""
                            MATCH (c:{card_type} {{id: '{card_id}'}})
                            MATCH (b) WHERE c <> b
                            WITH c, collect(b)[0..{overflow}] AS chosen UNWIND chosen AS b
                            MERGE (c)-[:{card_rule['rel_type']}]->(b)
                        """)
                        r = session.run(f"""
                            MATCH (c:{card_type} {{id: '{card_id}'}})-[r:{card_rule['rel_type']}]->(n)
                            WITH c, count(r) AS deg WHERE deg > {card_rule['limit']}
                            RETURN c
                        """)
                        if r.peek():
                            print(f"  [V6 ✓] cardinality  → {card_id}({card_type}) overflowed, "
                                  f"has edge to hub {hub_id}")
                            injected.append("cardinality")
                            # Query joins through the forced edge to return H
                            queries.append(
                                f"MATCH (c:{card_type} {{id: '{card_id}'}})"
                                f"-[r:{card_rule['rel_type']}]->(n) "
                                f"WITH c, count(r) AS deg WHERE deg > {card_rule['limit']} "
                                f"MATCH (c)-[:{card_rule['rel_type']}]"
                                f"->(h:{hub_type} {{id: '{hub_id}'}}) "
                                f"RETURN c, deg, h"
                            )
                else:
                    print(f"  [V6 –] cardinality  → no max_degree rule found")

        # Write detection queries
        with open("inconsistencies_overlap.txt", "w") as f:
            for q in queries:
                f.write(q + "\n")

        print(f"\n{'='*60}")
        print(f"Hub node : {hub_id} ({hub_type})")
        print(f"Run any query in inconsistencies_overlap.txt → hub appears")
        print(f"Violations injected: {injected}")
        print(f"Unique types: {len(set(injected))}/6")
        print(f"{'='*60}")
        return injected

    # =========================================================================
    # 5. EXPORT / LOAD ONTOLOGY
    # =========================================================================
    def export_ontology(self, filename="ontology_overlap.json"):
        data = {
            "triples": {
                "allowed":    [list(p) for p in self.allowed_patterns],
                "disallowed": [list(p) for p in self.disallowed_patterns]
            },
            "neighborhood_constraints": self.neighborhood_rules,
            "property_constraint":      self.property_constraint
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_ontology(self, filename="ontology_overlap.json"):
        with open(filename, "r") as f:
            data = json.load(f)
        self.allowed_patterns    = set(tuple(p) for p in data["triples"]["allowed"])
        self.disallowed_patterns = set(tuple(p) for p in data["triples"]["disallowed"])
        self.neighborhood_rules  = data["neighborhood_constraints"]
        self.property_constraint = data.get("property_constraint", None)


# =============================================================================
if __name__ == "__main__":
    gen = OverlapGenerator(
        "neo4j+ssc://3d49ba2d.databases.neo4j.io",
        ("neo4j", "swLRHNP8hZEyF8bSnFBJqZBuKXel2v4ZgqBgA_5a4Dg")
    )
    gen.clear_database()
    gen.generate_rules(num_allowed=20, num_disallowed=5)
    gen.generate_valid_graph(num_nodes=50)
    gen.inject_overlapping_violations()
    gen.export_ontology()
    gen.close()
