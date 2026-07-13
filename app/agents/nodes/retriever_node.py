from app.agents.state import Agentstate
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

class RetrieverNode:
    
    def __init__(self,retriever):
        self.retriever = retriever
        
    def retriever_node(self, state: Agentstate):
        try:
            ticket = state["ticket"]
            logger.info(f"RetrieverNode started with query: {ticket[:50]}...")

            docs = self.retriever.similarity_search(ticket)

            logger.info(f"RetrieverNode retrieved {len(docs)} documents.")

            for i, doc in enumerate(docs, 1):
                logger.debug(f"RetrieverNode Doc {i}: {doc.metadata}")

            return {
                "documents": docs
            }
        except Exception as e:
            logger.error(f"Error in RetrieverNode: {str(e)}")
            raise CustomException(f"RetrieverNode Failed", e)
