from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

ENTITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Entity Extraction Assistant.

Extract the following entities from the customer ticket.

Return ONLY the structured output.

Entities:
- order_id  (format: ORD-XXXX or TRK-XXXX)
- ticket_id (format: T-XXXX)
- user_id   (format: user_X)

Rules:
- If an entity is present in the current ticket, extract it directly.
- If the user says "it", "this order", "that ticket", look in the Conversation History for the most recent matching ID.
- Do not invent IDs.
- Preserve the original ID format exactly (e.g. ORD-1005, T-3012).
- If an entity is not found anywhere, return null."""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{ticket}"),
])