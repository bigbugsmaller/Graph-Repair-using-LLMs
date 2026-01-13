from langgraph.graph import StateGraph, START
from state import agent_state
import nodes
import config

if __name__ == "__main__":
    
    workflow = StateGraph(agent_state)
    
    workflow.add_node("manager", nodes.manager)
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("generate_repairs", nodes.generate_repairs)
    workflow.add_node("apply", nodes.apply)
    
    workflow.add_edge(START, "manager")
    
    # Add Conditional Edges
    workflow.add_conditional_edges(
        "manager",
        nodes.check1,
    )
    workflow.add_conditional_edges(
        "retrieve",
        nodes.check2,
    )
    workflow.add_edge("generate_repairs", "apply")
    workflow.add_conditional_edges(
        "apply",
        nodes.check3
    )

    # Compile the graph
    app = workflow.compile()
    
    print("Graph compiled successfully. Starting execution...")
    
    # Initial state
    initial_state = {
        "login_url": config.NEO4J_URI,
        "login_user": config.NEO4J_USERNAME,
        "login_password": config.NEO4J_PASSWORD,
        "results": [],
        "query": "",
        "status": ""
    }
    app.invoke(initial_state)

