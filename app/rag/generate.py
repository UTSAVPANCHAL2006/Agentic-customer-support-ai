from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.rag.llm import LLM

logger = get_logger(__name__)

from app.prompts.generate_prompt import GENERATE_PROMPT

class Generator:

    def __init__(self, llm):
        self.llm = llm

    def generate(
        self,
        ticket: str,
        action: str,
        documents=None,
        tool_result=None,
        history=None,
        order_id=None,
        ticket_id=None,
    ):

        if documents:
            context = "\n\n".join(
                doc.page_content
                for doc in documents
            )
        else:
            context = "No documents."

        if tool_result is None:
            tool_result = {}

        chain = GENERATE_PROMPT | self.llm

        payload = {
            "ticket": ticket,
            "action": action,
            "documents": context,
            "tool_result": str(tool_result),
            "history": history,
            "order_id": str(order_id) if order_id else "None",
            "ticket_id": str(ticket_id) if ticket_id else "None"
        }

        response = chain.invoke(payload)

        return response
        
    def stream_generate(
        self,
        ticket: str,
        action: str,
        documents=None,
        tool_result=None,
        history=None,
        order_id=None,
        ticket_id=None,
    ):
        if documents:
            context = "\n\n".join(doc.page_content for doc in documents)
        else:
            context = "No documents."

        if tool_result is None:
            tool_result = {}

        chain = GENERATE_PROMPT | self.llm

        payload = {
            "ticket": ticket,
            "action": action,
            "documents": context,
            "tool_result": str(tool_result),
            "history": history,
            "order_id": str(order_id) if order_id else "None",
            "ticket_id": str(ticket_id) if ticket_id else "None"
        }

        for chunk in chain.stream(payload):
            yield chunk.content
