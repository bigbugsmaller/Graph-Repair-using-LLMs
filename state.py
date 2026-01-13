from typing import TypedDict

class agent_state(TypedDict):
    login_url: str
    login_password: str
    login_user: str
    status: str
    repairs: str
    query: str
    results: list