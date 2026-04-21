from __future__ import annotations

from langgraph.graph import START, StateGraph

from graph_repair.workflow import nodes
from graph_repair.workflow.state import AgentState


def build_repair_app():
    workflow = StateGraph(AgentState)

    workflow.add_node("extract_schema", nodes.extract_schema)
    workflow.add_node("manager", nodes.manager)
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("generate_repairs", nodes.generate_repairs)
    workflow.add_node("apply", nodes.apply)

    workflow.add_edge(START, "extract_schema")
    workflow.add_edge("extract_schema", "manager")
    workflow.add_conditional_edges("manager", nodes.check_manager_status)
    workflow.add_conditional_edges("retrieve", nodes.evaluate_retrieval_results)
    workflow.add_edge("generate_repairs", "apply")
    workflow.add_conditional_edges("apply", nodes.verify_repairs)

    return workflow.compile()

