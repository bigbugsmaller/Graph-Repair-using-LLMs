# Neo4j Configuration
NEO4J_URI = "neo4j+s://02c07049.databases.neo4j.io"
NEO4J_USERNAME = "02c07049"
NEO4J_PASSWORD = "YxsPBfOGx1KyElg5Ck3omi95ZGXjHi8qiMEEb6W94rc"
NEO4J_DATABASE = "02c07049"

# Aura Configuration
AURA_INSTANCEID = "9738bd7b"
AURA_INSTANCENAME = "Instance01"
#"http://localhost:11434"
# Ollama Configuration
OLLAMA_HOST = "https://ollama.com"
OLLAMA_AUTH_HEADER = {'Authorization': 'Bearer 5c223e289b3a44dab9d3e35f2daf61f5.R3XOvVQZAAsKeSQaE4Gfxbd4'}
OLLAMA_MODEL = 'qwen3.5:cloud'
OLLAMA_SEED = 42          # Fixed seed → reproducible LLM outputs across benchmark runs
OLLAMA_TEMPERATURE = 0    # 0 = greedy/deterministic; raise (e.g. 0.7) for more creative responses

# Map URI to URL variable name used in logic
NEO4J_URL = NEO4J_URI
