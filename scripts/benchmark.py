import json

from _bootstrap import ensure_project_root

ensure_project_root()

from graph_repair.experiments.runner import run_experiment


if __name__ == "__main__":
    results = run_experiment()
    print(json.dumps(results, indent=4))
