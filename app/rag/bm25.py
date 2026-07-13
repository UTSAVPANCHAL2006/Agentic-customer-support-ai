from langchain_community.retrievers import BM25Retriever

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


class BM25:

    def create_retriever(self, documents):
        try:
            logger.info("Creating BM25 Retriever")
            
            retriever = BM25Retriever.from_documents(documents)
            retriever.k = 2
            
            logger.info("BM25 Retriever created successfully")
            
            return retriever
        
        except Exception as e:
            logger.error("Failed to create BM25 Retriever")
            raise CustomException(e)