from __future__ import annotations

import logging
import re
from typing import Literal

import config
from graph_repair.db import GraphDB
from graph_repair.llm.client import get_llm_client, stream_chat_text
from graph_repair.prompts.repair import build_description_prompt, build_repair_prompt
from graph_repair.schema import get_schema, get_structured_schema
from graph_repair.workflow.state import AgentState
from langgraph.graph import END


_CYPHER_START_RE = re.compile(
    r"\b(MATCH|MERGE|CREATE|DELETE|DETACH|SET|REMOVE|WITH|CALL|UNWIND)\b",
    re.IGNORECASE,
)


def _get_llm_client():
    return get_llm_client()


def extract_schema(state: AgentState):
    logging.info("Extracting graph schema preprocessing...")
    db = GraphDB(
        state["login_url"],
        state["login_user"],
        state["login_password"],
        config.NEO4J_DATABASE,
    )
    try:
        output = get_structured_schema(db)
        database_description = get_schema(output)
    finally:
        db.close()

    logging.info("Schema generated successfully.")
    return {"database_description": database_description}


def describe_query(state: AgentState, query: str) -> str:
    print("The Description of the Input:")
    prompt = build_description_prompt(state["database_description"], query)
    return stream_chat_text(prompt)


def query_is_correct(text: str) -> str:
    cleaned = text.replace("```cypher", "").replace("```", "").strip()
    match = _CYPHER_START_RE.search(cleaned)
    if match:
        cleaned = cleaned[match.start() :]
    semicolon = cleaned.find(";")
    if semicolon != -1:
        cleaned = cleaned[: semicolon + 1]
    cleaned = " ".join(cleaned.split())
    print(cleaned)
    return cleaned


def generate_repairs(state: AgentState):
    formatted_inconsistency = describe_query(state, state["query"])
    print("The Generated Query for repair:\n")
    repair_text = stream_chat_text(
        build_repair_prompt(state["database_description"], formatted_inconsistency)
    )
    print(repair_text)
    repairs = query_is_correct(repair_text)
    return {"repairs": repairs}


def retrieve(state: AgentState):
    db = GraphDB(
        state["login_url"],
        state["login_user"],
        state["login_password"],
        config.NEO4J_DATABASE,
    )
    try:
        return {"results": db.run_query(state["query"])}
    finally:
        db.close()


def apply(state: AgentState):
    db = GraphDB(
        state["login_url"],
        state["login_user"],
        state["login_password"],
        config.NEO4J_DATABASE,
    )
    try:
        db.run_query(state["repairs"])
    finally:
        db.close()
    return {}


def manager(state: AgentState):
    logging.basicConfig(
        level=logging.INFO,
        filename="log.log",
        filemode="w",
        format="%(asctime)s -%(levelname)s -%(message)s",
    )

    list_of_inconsistencies = state["list_of_inconsistencies"]
    cycle_count = state.get("cycle_count", 0)
    max_cycles = 5

    if len(list_of_inconsistencies) == 0 or cycle_count >= max_cycles:
        if cycle_count >= max_cycles:
            logging.warning("Manager exited due to cycle limit (%d).", max_cycles)
        else:
            logging.info("Manager initiated exit.")
        return {"status": "EXIT", "cycle_count": cycle_count + 1}

    message = list_of_inconsistencies.pop()
    logging.info("Manager selected inconsistency query: %s", message)
    return {"status": "Processing", "query": message, "cycle_count": cycle_count + 1}


def check_manager_status(state: AgentState) -> Literal[END, "retrieve"]:
    logging.info("Checking whether the workflow should exit.")
    if state["status"] == "EXIT":
        print("You have exited the process.")
        logging.info("Successfully exited.")
        return END
    return "retrieve"


def evaluate_retrieval_results(state: AgentState) -> Literal["manager", "generate_repairs"]:
    logging.info("Checking whether the inconsistency exists in the graph.")
    if len(state["results"]) == 0:
        print("No such patterns in the knowledge graph.")
        return "manager"
    return "generate_repairs"


def verify_repairs(state: AgentState) -> Literal["manager", "generate_repairs"]:
    logging.info("Verifying whether repairs resolved the inconsistency.")
    db = GraphDB(
        state["login_url"],
        state["login_user"],
        state["login_password"],
        config.NEO4J_DATABASE,
    )
    try:
        results = db.run_query(state["query"])
    finally:
        db.close()

    if len(results) == 0:
        print("Repairs were done.")
        return "manager"
    return "generate_repairs"

