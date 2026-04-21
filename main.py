from pathlib import Path

import config
from graph_repair.seed import init_seed
from graph_repair.workflow.app import build_repair_app

init_seed()


def _load_inconsistencies() -> list[str]:
    for filename in ("inconsistency.txt", "inconsistencies.txt"):
        path = Path(filename)
        if path.exists():
            return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    raise FileNotFoundError("Expected inconsistency.txt or inconsistencies.txt in the project root.")


if __name__ == "__main__":
    app = build_repair_app()
    print("Graph compiled successfully. Starting execution...")

    initial_state = {
        "login_url": config.NEO4J_URI,
        "login_user": config.NEO4J_USERNAME,
        "login_password": config.NEO4J_PASSWORD,
        "results": [],
        "query": "",
        "status": "",
        "repairs": "",
        "database_description": "",
        "cycle_count": 0,
        "total_tokens": 0,
        "list_of_inconsistencies": _load_inconsistencies(),
    }

    app.invoke(initial_state)



