import logging
import re
from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from neo4j.exceptions import ClientError, CypherSyntaxError
from graph_repair.db import GraphDB
from graph_repair.workflow.agent.state import AgentState
from ollama import Client
import config
from graph_repair.prompts.query_generation import DESCRIBE_QUERY_PROMPT, GENERATE_REPAIRS_PROMPT

log = logging.getLogger("agent.tools")

_CYPHER_START_RE = re.compile(
    r"\b(MATCH|MERGE|CREATE|DELETE|DETACH|SET|REMOVE|WITH|CALL|UNWIND)\b",
    re.IGNORECASE,
)


def _clean_cypher(raw: str) -> str:
    """Strip markdown fences and trim to the first complete Cypher statement."""
    cleaned = raw.replace("```cypher", "").replace("```", "").strip()
    match = _CYPHER_START_RE.search(cleaned)
    if match:
        cleaned = cleaned[match.start():]
    semicolon = cleaned.find(";")
    if semicolon != -1:
        cleaned = cleaned[: semicolon + 1]
    return " ".join(cleaned.split())

@tool
def retrieve_inconsistency(cypher_query:str, state: Annotated[AgentState, InjectedState]) -> str:
    """Run a Cypher MATCH query to detect whether an inconsistency pattern is
    still present in the graph.
    Args:
        cypher_query: A read-only Cypher MATCH statement describing the
                      inconsistency pattern to detect.
    """
    log.info("retrieve_inconsistency | query=%.120s", cypher_query)
    db = GraphDB(state["login_url"], state["login_user"], state["login_password"])
    try:
        results = db.run_query(cypher_query)
    except Exception as exc:
        log.error("retrieve_inconsistency failed: %s", exc)
        return f"ERROR running detection query: {exc}"
    finally:
        #do we need this as session takes care of it  
        db.close()

    if len(results) == 0:
        return "No rows matched — inconsistency is NOT present in the graph."
    
    return (
         f"Row(s) matched ({len(results)}) — inconsistency IS present. Please proceed with the repair."
    )

@tool
def validate_repair_query(repair_query: str, state: Annotated[AgentState, InjectedState]) -> str:
    """Validate the syntax of a proposed Cypher repair query using Neo4j's
    EXPLAIN command.  Always call this before apply_repair_query.

    Args:
        repair_query: The Cypher write query you intend to apply as a repair.
    """
    cleaned = _clean_cypher(repair_query)
    log.info("validate_repair_query | query=%.120s", cleaned)
    db = GraphDB(state["login_url"], state["login_user"], state["login_password"])
    try:
        db.run_query("EXPLAIN " + cleaned)
        return f"VALID — query passes syntax check.\nQuery: {cleaned}"
    except CypherSyntaxError as exc:
        return f"INVALID — Cypher syntax error: {exc}\nQuery: {cleaned}"
    except ClientError as exc:
        return f"INVALID — Neo4j client error: {exc}\nQuery: {cleaned}"
    except Exception as exc:
        return f"INVALID — Unexpected error: {exc}\nQuery: {cleaned}"
    finally:
        db.close()



@tool
def apply_repair_query(repair_query: str, state: Annotated[AgentState, InjectedState]) -> str:
    """Execute a Cypher write query to repair an inconsistency in the Neo4j
    graph.  Only call this after validate_repair_query confirms VALID.

    Args:
        repair_query: The validated Cypher write query to execute.
    """
    cleaned = _clean_cypher(repair_query)
    log.info("apply_repair_query | query=%.120s", cleaned)
    db = GraphDB(state["login_url"], state["login_user"], state["login_password"])
    try:
        db.run_query(cleaned)
        log.info("Repair applied successfully.")
        return f"SUCCESS — repair query executed.\nQuery: {cleaned}"
    except CypherSyntaxError as exc:
        return f"FAILED — Cypher syntax error during apply: {exc}"
    except ClientError as exc:
        return f"FAILED — Neo4j client error during apply: {exc}"
    except Exception as exc:
        return f"FAILED — Unexpected error during apply: {exc}"
    finally:
        db.close()

@tool
def verify_repair(cypher_query: str, state: Annotated[AgentState, InjectedState]) -> str:
    """Re-run the original inconsistency detection query after a repair to
    confirm the inconsistency has been resolved.

    Args:
        cypher_query: The same detection query used in retrieve_inconsistency.
    """
    log.info("verify_repair | query=%.120s", cypher_query)
    db = GraphDB(state["login_url"], state["login_user"], state["login_password"])
    try:
        results = db.run_query(cypher_query)
    except Exception as exc:
        log.error("verify_repair failed: %s", exc)
        return f"ERROR during verification: {exc}"
    finally:
        db.close()

    if len(results) == 0:
        return "RESOLVED — inconsistency is no longer present after repair."
    return (
        f"UNRESOLVED — {len(results)} row(s) still match the inconsistency "
        "pattern. Try generating a different repair query."
    )


@tool
def generate_repair(state: Annotated[AgentState, InjectedState]) -> str:
    """Generate a Cypher repair query based on the current inconsistency pattern and database description.
    Call this tool when you need a suggested repair query from the specialized repair generation model.
    """
    query = state.get("query", "")
    database_description = state.get("database_description", "")
    
    if not query or not database_description:
        return "ERROR: Missing query or database description in state."

    try:
        client = Client(
            host=config.OLLAMA_HOST,
            headers=config.OLLAMA_AUTH_HEADER
        )
    except Exception as e:
        log.error("Failed connection to Ollama: %s", e, exc_info=True)
        return f"ERROR: Failed connection to Ollama: {e}"

    log.info("generate_repair | query=%.120s", query)
    
    # Generate repair directly from raw query
    fquestion_rep = GENERATE_REPAIRS_PROMPT.format(
        database_description=database_description,
        formatted_inconsistency=f" detected by this query: {query}"
    )
    messages_rep = [{"role": "user", "content": fquestion_rep}]
    
    _llm_opts = {"seed": config.OLLAMA_SEED, "temperature": config.OLLAMA_TEMPERATURE}
    log.info("generate_repair | generating Cypher repair for query: %.80s", query)
    response_rep = client.chat(config.OLLAMA_MODEL, messages=messages_rep, options=_llm_opts)
    repairs = response_rep.get('message', {}).get('content', '')
        
    cleaned = _clean_cypher(repairs)
    log.info("generate_repair | generated query=%.120s", cleaned)
    
    return f"Suggested Repair Query:\n```cypher\n{cleaned}\n```"


GRAPH_REPAIR_TOOLS = [
    retrieve_inconsistency,
    validate_repair_query,
    apply_repair_query,
    verify_repair,
    generate_repair,
]
