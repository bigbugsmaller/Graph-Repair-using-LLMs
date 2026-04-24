import logging
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode
from graph_repair.workflow.agent.system_prompt import _SYSTEM_PROMPT
import config
from graph_repair.workflow.agent.state import AgentState
from graph_repair.workflow.agent.tools import GRAPH_REPAIR_TOOLS

log = logging.getLogger("agent.node")

def agent_node(state: AgentState) -> dict:
    """Tool-calling LLM node.
    On the very first call for a given inconsistency (messages is empty),
    seeds the conversation with a system message and a user message that
    contains the detection query and graph schema.

    On subsequent calls (after tool results have been appended), passes the
    accumulated messages straight back to the LLM.
    """
    llm = ChatOllama( 
        model=config.OLLAMA_MODEL,
        temperature=config.OLLAMA_TEMPERATURE,
        seed=config.OLLAMA_SEED,
        base_url=config.OLLAMA_HOST,
        client_kwargs={'headers': config.OLLAMA_AUTH_HEADER},
    ).bind_tools(GRAPH_REPAIR_TOOLS)
    
    messages = state.get("messages", [])
    status = state.get("status", "").lower()
    
    if not messages:
        # Fresh Start: New query dispatched by Manager
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Schema:\n{state.get('database_description', '')}\n\n"
                f"Query:\n{state.get('query', '')}"
            ))
        ]
    elif status == "processing":
        # Retry logic: Manager sent us back here because the repair didn't work
        if state.get("cycle_count", 0) > 5:
            return {"status": "next_query", "cycle_count": 0}
            
        messages = messages + [
            HumanMessage(content="The previous repair attempt failed. Check the schema and retry.")
        ]
    # If status is "active", we just keep the messages as they are (containing tool results)

    response = llm.invoke(messages)
    
    # Print the agent's raw response to the console
    if hasattr(response, "content") and response.content:
        print(f"\n[Agent Response]:\n{response.content}\n")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"\n[Agent Tool Calls]:\n{response.tool_calls}\n")
        
    return {
        "messages": messages + [response],
        "cycle_count": state.get("cycle_count", 0) + 1,
        "status": "active" # Reset from 'processing' until tools fail again
    }


def should_continue(state: AgentState) -> Literal["tools", "manager"]:
    """Route after agent_node.
    Tells the agent where it should go after 
    """
    if state.get("status") == "next_query":
        return "manager"

    messages = state.get("messages", [])
    if messages and hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
        return "tools"
    
    return "manager" 

repair_tool_node = ToolNode(GRAPH_REPAIR_TOOLS)
