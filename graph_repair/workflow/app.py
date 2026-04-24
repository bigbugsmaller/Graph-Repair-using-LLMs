from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from graph_repair.workflow.agent import nodes
from graph_repair.workflow.agent import agent
from graph_repair.workflow.agent.state import AgentState
from graph_repair.workflow.agent.tools import GRAPH_REPAIR_TOOLS


def build_repair_app():
    """Compile and return the agentic repair StateGraph."""
    workflow = StateGraph(AgentState)
    workflow.add_node("extract_schema", nodes.extract_schema)
    workflow.add_node("manager", nodes.manager)
    workflow.add_node("agent_node", agent.agent_node)
    workflow.add_node("tools", ToolNode(GRAPH_REPAIR_TOOLS))

    workflow.add_edge(START, "extract_schema")
    workflow.add_edge("extract_schema", "manager")
    workflow.add_conditional_edges("manager", nodes.check_manager_status, {
        END: END,
        "agent_node": "agent_node", 
    })
    workflow.add_conditional_edges("agent_node", agent.should_continue, {
        "tools": "tools",
        "manager": "manager",
    })

    workflow.add_edge("tools", "agent_node")
    return workflow.compile()



if __name__=="__main__":
    app=build_repair_app()
    result=app.invoke({
        "login_url": "bolt://localhost:7687",
        "login_password": "password",
        "login_user": "neo4j",
        "query": "MATCH (a:Movie)<-[:ACTED_IN]-(b:Person) RETURN a.title, b.name",
    })
    print(result)
