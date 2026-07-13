from typing import TypedDict , Annotated
from langchain_core.documents import Document
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Agentstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    ticket : str
    category : str
    urgency : str
    sentiment : str
    action : str  
    tool_name : str
    documents : list[Document]
    tool_result: dict
    response : str
    order_id: str | None
    ticket_id: str | None
    user_id: str | None
