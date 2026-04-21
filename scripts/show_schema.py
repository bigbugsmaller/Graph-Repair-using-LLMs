from _bootstrap import ensure_project_root

ensure_project_root()

import config
from graph_repair.db import GraphDB
from graph_repair.schema import get_schema, get_structured_schema


if __name__ == "__main__":
    db = GraphDB(
        config.NEO4J_URI,
        config.NEO4J_USERNAME,
        config.NEO4J_PASSWORD,
        config.NEO4J_DATABASE,
    )
    try:
        output = get_structured_schema(db)
        schema = get_schema(output)
        print(schema)
    finally:
        db.close()
