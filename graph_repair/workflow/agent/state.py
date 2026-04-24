from typing import TypedDict

class AgentState(TypedDict):
    login_url: str
    login_password: str
    login_user: str

    status: str
    repairs: str
    query: str
    results: list
    list_of_inconsistencies: list
    database_description: str

    cycle_count: int
    total_tokens: int
    iteration_count: int
    #convergence 
    repair_status_array: list
    prev_repair_status_array: list
    current_index: int
    messages: list









    