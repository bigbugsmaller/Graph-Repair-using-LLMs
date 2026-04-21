from __future__ import annotations


def build_description_prompt(database_description: str, query: str) -> str:
    return f"""
{database_description}
Describe this query in detail as a short paragraph:
{query}

Return only the paragraph.
""".strip()


def build_repair_prompt(database_description: str, inconsistency_description: str) -> str:
    return f"""
{database_description}
The database has inconsistencies that we want to remove.
One such inconsistency is: {inconsistency_description}.

Generate ONE Cypher query to fix this inconsistency.
The query should:
1. MATCH the pattern described above.
2. DELETE, DETACH DELETE, or update the incorrect relationship or node.
3. Make only one repair action.

IMPORTANT:
- Return ONLY the Cypher query, nothing else.
- No explanations, no comments, no markdown.
- Start directly with MATCH, MERGE, DELETE, DETACH, SET, or WITH.
- End with a semicolon.
- Only ONE query.
""".strip()

