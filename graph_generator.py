"""
Fictitious Graph Generator for Neo4j

Supports two modes:
1. Parametric: Generate N nodes and E edges with abstract names
2. Schema-driven: Generate graphs from YAML config with domain-specific ontologies

Inspired by NetworkX but with Neo4j persistence and Faker integration.
"""

import random
import yaml
from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path
from neo4j import GraphDatabase
from faker import Faker
import config


class GraphGenerator:
    """Generate fictitious graphs and persist them to Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """
        Initialize the graph generator with Neo4j connection.
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.faker = Faker()
        
        # Register custom Faker providers for Academic and Health domains
        self._register_custom_providers()
    
    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()
    
    def _register_custom_providers(self):
        """Register custom Faker providers for specialized domains"""
        # Academic domain data
        self.academic_data = {
            'departments': ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 
                          'Biology', 'Engineering', 'Medicine', 'Business', 'Psychology'],
            'courses': ['Introduction to {}', 'Advanced {}', '{} Fundamentals', 
                       '{} Theory', 'Applied {}', '{} Laboratory'],
            'course_subjects': ['Algorithms', 'Data Structures', 'Calculus', 'Statistics',
                              'Quantum Mechanics', 'Organic Chemistry', 'Genetics', 
                              'Machine Learning', 'Database Systems'],
            'degrees': ['Bachelor', 'Master', 'PhD', 'Associate'],
            'majors': ['Computer Science', 'Mathematics', 'Physics', 'Biology', 
                      'Engineering', 'Business Administration']
        }
        
        # Health domain data
        self.health_data = {
            'specialties': ['Cardiology', 'Neurology', 'Oncology', 'Pediatrics', 
                          'Orthopedics', 'Dermatology', 'Psychiatry', 'Radiology'],
            'conditions': ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 
                         'Depression', 'Anxiety', 'Migraine', 'Allergies'],
            'medications': ['Aspirin', 'Ibuprofen', 'Metformin', 'Lisinopril',
                          'Atorvastatin', 'Omeprazole', 'Sertraline'],
            'departments': ['Emergency', 'ICU', 'Surgery', 'Outpatient', 
                          'Laboratory', 'Radiology', 'Pharmacy']
        }
    
    def _prompt_user_for_wipe(self) -> bool:
        """
        Prompt user whether to wipe existing database.
        
        Returns:
            True if user wants to wipe, False otherwise
        """
        while True:
            response = input("\n⚠️  Wipe existing database before generating graph? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def _wipe_database(self):
        """Delete all nodes and relationships from the database"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database wiped clean")
    
    def _evaluate_faker_expression(self, expr: str) -> Any:
        """
        Evaluate a Faker expression or custom domain expression.
        
        Args:
            expr: Expression like "faker.name()" or "academic.department"
            
        Returns:
            Generated value
        """
        if not isinstance(expr, str):
            return expr
            
        if expr.startswith('faker.'):
            # Standard Faker method
            method_name = expr.replace('faker.', '').strip('()')
            if hasattr(self.faker, method_name):
                method = getattr(self.faker, method_name)
                return method()
            else:
                return expr
        
        elif expr.startswith('academic.'):
            # Academic domain
            field = expr.replace('academic.', '')
            if field == 'department':
                return random.choice(self.academic_data['departments'])
            elif field == 'course':
                template = random.choice(self.academic_data['courses'])
                subject = random.choice(self.academic_data['course_subjects'])
                return template.format(subject)
            elif field == 'degree':
                return random.choice(self.academic_data['degrees'])
            elif field == 'major':
                return random.choice(self.academic_data['majors'])
            elif field == 'gpa':
                return round(random.uniform(2.0, 4.0), 2)
            elif field == 'credits':
                return random.randint(1, 4)
            else:
                return expr
        
        elif expr.startswith('health.'):
            # Health domain
            field = expr.replace('health.', '')
            if field == 'specialty':
                return random.choice(self.health_data['specialties'])
            elif field == 'condition':
                return random.choice(self.health_data['conditions'])
            elif field == 'medication':
                return random.choice(self.health_data['medications'])
            elif field == 'department':
                return random.choice(self.health_data['departments'])
            elif field == 'blood_pressure':
                return f"{random.randint(90, 180)}/{random.randint(60, 120)}"
            elif field == 'temperature':
                return round(random.uniform(36.0, 39.0), 1)
            else:
                return expr
        
        elif expr.startswith('random.int('):
            # Parse random.int(min, max)
            import re
            match = re.match(r'random\.int\((\d+),\s*(\d+)\)', expr)
            if match:
                min_val, max_val = int(match.group(1)), int(match.group(2))
                return random.randint(min_val, max_val)
            return expr
        
        elif expr.startswith('random.float('):
            # Parse random.float(min, max)
            import re
            match = re.match(r'random\.float\(([\d.]+),\s*([\d.]+)\)', expr)
            if match:
                min_val, max_val = float(match.group(1)), float(match.group(2))
                return round(random.uniform(min_val, max_val), 2)
            return expr
        
        else:
            return expr
    
    def generate_parametric(
        self, 
        num_nodes: int, 
        num_edges: int,
        node_prefix: str = "Node",
        edge_prefix: str = "R",
        wipe_db: Optional[bool] = None
    ) -> Dict[str, int]:
        """
        Generate a random graph with N nodes and E edges using abstract names.
        
        Args:
            num_nodes: Number of nodes to create
            num_edges: Number of edges to create
            node_prefix: Prefix for node names (default: "Node")
            edge_prefix: Prefix for relationship types (default: "R")
            wipe_db: Whether to wipe database (None = prompt user)
            
        Returns:
            Dictionary with generation statistics
        """
        if wipe_db is None:
            wipe_db = self._prompt_user_for_wipe()
        
        if wipe_db:
            self._wipe_database()
        
        print(f"\n🔨 Generating parametric graph: {num_nodes} nodes, {num_edges} edges")
        
        with self.driver.session(database=self.database) as session:
            # Create nodes
            print(f"Creating {num_nodes} nodes...")
            for i in range(1, num_nodes + 1):
                session.run(
                    f"CREATE (n:{node_prefix} {{id: $id, name: $name}})",
                    id=i,
                    name=f"{node_prefix}{i}"
                )
            
            # Create edges using random algorithm
            print(f"Creating {num_edges} edges...")
            edges_created = 0
            max_attempts = num_edges * 10  # Prevent infinite loops
            attempts = 0
            
            while edges_created < num_edges and attempts < max_attempts:
                attempts += 1
                # Random edge selection
                node1_id = random.randint(1, num_nodes)
                node2_id = random.randint(1, num_nodes)
                
                # Avoid self-loops
                if node1_id == node2_id:
                    continue
                
                # Create relationship
                rel_type = f"{edge_prefix}{edges_created + 1}"
                result = session.run(f"""
                    MATCH (a:{node_prefix} {{id: $id1}}), (b:{node_prefix} {{id: $id2}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    RETURN r
                """, id1=node1_id, id2=node2_id)
                
                if result.single():
                    edges_created += 1
            
            print(f"✓ Created {num_nodes} nodes and {edges_created} edges")
            
            return {
                'nodes_created': num_nodes,
                'edges_created': edges_created,
                'edge_prefix': edge_prefix,
                'node_prefix': node_prefix
            }
    
    def generate_from_config(
        self, 
        config_path: str,
        wipe_db: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Generate a graph from a YAML configuration file.
        
        Args:
            config_path: Path to YAML config file
            wipe_db: Whether to wipe database (None = prompt user)
            
        Returns:
            Dictionary with generation statistics
        """
        if wipe_db is None:
            wipe_db = self._prompt_user_for_wipe()
        
        if wipe_db:
            self._wipe_database()
        
        # Load YAML config
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            graph_config = yaml.safe_load(f)
        
        print(f"\n🔨 Generating graph from config: {config_path}")
        
        stats = {
            'nodes_created': 0,
            'edges_created': 0,
            'node_types': {},
            'edge_types': {}
        }
        
        # Track created nodes by label for relationship creation
        node_ids_by_label: Dict[str, List[int]] = {}
        
        with self.driver.session(database=self.database) as session:
            # Create nodes
            if 'nodes' in graph_config:
                for node_spec in graph_config['nodes']:
                    label = node_spec['label']
                    count = node_spec.get('count', 1)
                    properties = node_spec.get('properties', {})
                    
                    print(f"Creating {count} {label} nodes...")
                    node_ids_by_label[label] = []
                    
                    for i in range(count):
                        # Evaluate property expressions
                        props = {}
                        for key, value in properties.items():
                            props[key] = self._evaluate_faker_expression(value)
                        
                        # Create node and get its ID
                        result = session.run(
                            f"CREATE (n:{label} $props) RETURN id(n) as node_id",
                            props=props
                        )
                        node_id = result.single()['node_id']
                        node_ids_by_label[label].append(node_id)
                        stats['nodes_created'] += 1
                    
                    stats['node_types'][label] = count
            
            # Create edges
            if 'edges' in graph_config:
                for edge_spec in graph_config['edges']:
                    rel_type = edge_spec['type']
                    from_label = edge_spec['from']
                    to_label = edge_spec['to']
                    count = edge_spec.get('count', 1)
                    direction = edge_spec.get('direction', 'unidirectional')
                    weighted = edge_spec.get('weighted', False)
                    weight_range = edge_spec.get('weight_range', [0.0, 1.0])
                    properties = edge_spec.get('properties', {})
                    
                    print(f"Creating {count} {rel_type} relationships...")
                    
                    from_nodes = node_ids_by_label.get(from_label, [])
                    to_nodes = node_ids_by_label.get(to_label, [])
                    
                    if not from_nodes or not to_nodes:
                        print(f"⚠️  Skipping {rel_type}: missing nodes for {from_label} or {to_label}")
                        continue
                    
                    for _ in range(count):
                        from_id = random.choice(from_nodes)
                        to_id = random.choice(to_nodes)
                        
                        # Evaluate edge properties
                        edge_props = {}
                        for key, value in properties.items():
                            edge_props[key] = self._evaluate_faker_expression(value)
                        
                        # Add weight if specified
                        if weighted:
                            edge_props['weight'] = round(
                                random.uniform(weight_range[0], weight_range[1]), 3
                            )
                        
                        # Create relationship
                        session.run(f"""
                            MATCH (a), (b)
                            WHERE id(a) = $from_id AND id(b) = $to_id
                            MERGE (a)-[r:{rel_type} $props]->(b)
                        """, from_id=from_id, to_id=to_id, props=edge_props)
                        
                        stats['edges_created'] += 1
                        
                        # Create bidirectional if specified
                        if direction == 'bidirectional':
                            session.run(f"""
                                MATCH (a), (b)
                                WHERE id(a) = $from_id AND id(b) = $to_id
                                MERGE (b)-[r:{rel_type} $props]->(a)
                            """, from_id=from_id, to_id=to_id, props=edge_props)
                            stats['edges_created'] += 1
                    
                    stats['edge_types'][rel_type] = count
        
        print(f"✓ Created {stats['nodes_created']} nodes and {stats['edges_created']} edges")
        return stats


def main():
    """CLI entry point for graph generation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate fictitious graphs for Neo4j',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parametric mode: 100 nodes, 500 edges
  python graph_generator.py --nodes 100 --edges 500
  
  # Custom prefixes
  python graph_generator.py --nodes 50 --edges 200 --node-prefix Person --edge-prefix Knows
  
  # Schema-driven mode from YAML
  python graph_generator.py --config examples/academic_graph.yaml
  
  # Auto-wipe database
  python graph_generator.py --config examples/health_graph.yaml --wipe
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--nodes', type=int, help='Number of nodes (parametric mode)')
    mode_group.add_argument('--config', type=str, help='Path to YAML config file (schema-driven mode)')
    
    # Parametric mode options
    parser.add_argument('--edges', type=int, help='Number of edges (required with --nodes)')
    parser.add_argument('--node-prefix', type=str, default='Node', help='Node name prefix (default: Node)')
    parser.add_argument('--edge-prefix', type=str, default='R', help='Edge type prefix (default: R)')
    
    # Database options
    parser.add_argument('--wipe', action='store_true', help='Wipe database without prompting')
    parser.add_argument('--no-wipe', action='store_true', help='Keep existing data without prompting')
    parser.add_argument('--uri', type=str, help='Neo4j URI (default: from config.py)')
    parser.add_argument('--user', type=str, help='Neo4j username (default: from config.py)')
    parser.add_argument('--password', type=str, help='Neo4j password (default: from config.py)')
    
    args = parser.parse_args()
    
    # Validate parametric mode
    if args.nodes and not args.edges:
        parser.error("--edges is required when using --nodes")
    
    # Determine wipe behavior
    wipe_db = None
    if args.wipe:
        wipe_db = True
    elif args.no_wipe:
        wipe_db = False
    
    # Get Neo4j credentials
    uri = args.uri or config.NEO4J_URI
    user = args.user or config.NEO4J_USERNAME
    password = args.password or config.NEO4J_PASSWORD
    
    if not all([uri, user, password]):
        print("❌ Error: Neo4j credentials not found. Set them in .env or use --uri, --user, --password")
        return 1
    
    # Initialize generator
    generator = GraphGenerator(uri, user, password)
    
    try:
        if args.nodes:
            # Parametric mode
            stats = generator.generate_parametric(
                num_nodes=args.nodes,
                num_edges=args.edges,
                node_prefix=args.node_prefix,
                edge_prefix=args.edge_prefix,
                wipe_db=wipe_db
            )
            print(f"\n✅ Parametric generation complete!")
            print(f"   Nodes: {stats['nodes_created']} ({stats['node_prefix']}1..{stats['node_prefix']}{stats['nodes_created']})")
            print(f"   Edges: {stats['edges_created']} ({stats['edge_prefix']}1..{stats['edge_prefix']}{stats['edges_created']})")
        
        else:
            # Schema-driven mode
            stats = generator.generate_from_config(
                config_path=args.config,
                wipe_db=wipe_db
            )
            print(f"\n✅ Schema-driven generation complete!")
            print(f"   Total nodes: {stats['nodes_created']}")
            print(f"   Total edges: {stats['edges_created']}")
            print(f"   Node types: {', '.join(f'{k}({v})' for k, v in stats['node_types'].items())}")
            print(f"   Edge types: {', '.join(f'{k}({v})' for k, v in stats['edge_types'].items())}")
    
    finally:
        generator.close()
    
    return 0


if __name__ == '__main__':
    exit(main())
