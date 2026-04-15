from _bootstrap import ensure_project_root

ensure_project_root()

from graph_repair.experiments.snapshot import export_snapshot


if __name__ == "__main__":
    export_snapshot()
