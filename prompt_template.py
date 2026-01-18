prompt_template = """
Instructions:
Generate Cypher statement to query a graph database to get the data to answer 
the following user question.
Graph database schema:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided in 
the schema.
{schema}
Terminology mapping:
This section is helpful to map terminology between the user question and the 
graph database schema.
{terminology}
Examples:
The following examples provide useful patterns for querying the graph database.
{examples}
Format instructions:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to
construct a Cypher statement.
Do not include any text except the generated Cypher statement.
ONLY RESPOND WITH CYPHER—NO CODE BLOCKS.
User question: {question}
"""