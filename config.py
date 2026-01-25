from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv(Path(__file__).with_name(".env"))


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# Neo4j Configuration
NEO4J_URI = _env("NEO4J_URI")
NEO4J_USERNAME = _env("NEO4J_USERNAME")
NEO4J_PASSWORD = _env("NEO4J_PASSWORD")
NEO4J_DATABASE = _env("NEO4J_DATABASE", "neo4j")

# Map URI to URL variable name used in logic
NEO4J_URL = NEO4J_URI

# Aura Configuration (optional)
AURA_INSTANCEID = _env("AURA_INSTANCEID")
AURA_INSTANCENAME = _env("AURA_INSTANCENAME")

# Ollama Configuration
OLLAMA_HOST = _env("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.1")
_ollama_token = _env("OLLAMA_BEARER_TOKEN")
OLLAMA_AUTH_HEADER = {"Authorization": f"Bearer {_ollama_token}"} if _ollama_token else {}
