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
# TODO: Should standardize and keep only one of these
NEO4J_URL = NEO4J_URI

# Aura Configuration (optional)
AURA_INSTANCEID = _env("AURA_INSTANCEID")
AURA_INSTANCENAME = _env("AURA_INSTANCENAME")

# LLM Provider Configuration
# Options: "ollama" (default) or "lm-studio"
LLM_PROVIDER = _env("LLM_PROVIDER", "ollama")

# Ollama Configuration
OLLAMA_HOST = _env("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.1")
_ollama_token = _env("OLLAMA_BEARER_TOKEN")
OLLAMA_AUTH_HEADER = {"Authorization": f"Bearer {_ollama_token}"} if _ollama_token else {}

# LM Studio Configuration
LM_STUDIO_HOST = _env("LM_STUDIO_HOST", "http://localhost:1234")
LM_STUDIO_MODEL = _env("LM_STUDIO_MODEL", "meta-llama-3.1-8b-instruct")

# Reproducibility
# Set RANDOM_SEED to any integer for deterministic graph generation and experiment runs.
# Leave empty or unset for non-deterministic behaviour.
_seed_raw = _env("RANDOM_SEED")
RANDOM_SEED: int | None = int(_seed_raw) if _seed_raw else None

# LLM seed passed to Ollama ("seed" option) and LM Studio ("seed" param).
# Only effective when the model/provider honours it. Defaults to RANDOM_SEED.
_llm_seed_raw = _env("LLM_SEED")
LLM_SEED: int | None = int(_llm_seed_raw) if _llm_seed_raw else RANDOM_SEED

# Convenience aliases used by workflow nodes and the agentic layer.
# OLLAMA_SEED mirrors LLM_SEED; OLLAMA_TEMPERATURE controls LLM randomness.
OLLAMA_SEED: int | None = LLM_SEED
OLLAMA_TEMPERATURE: float = float(_env("OLLAMA_TEMPERATURE", "0"))
