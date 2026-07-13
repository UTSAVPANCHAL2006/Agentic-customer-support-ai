from langchain_huggingface import HuggingFaceEmbeddings

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import EMBEDDING_MODEL

logger = get_logger(__name__)


class Embedding:
    
    def __init__(self, model_name: str):
        
        try:
            logger.info(f"Loading embedding model: {model_name}")
            
            self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
            logger.info("Embedding model loaded successfully.")
            
        except Exception as e:
            logger.error("Failed to load embedding model.")
            raise CustomException(e)
        
    def get_embedding(self):
        
        return self.embedding_model
    
if __name__ == "__main__":
    
    embedding = Embedding(model_name=EMBEDDING_MODEL)
    
    model = embedding.get_embedding()