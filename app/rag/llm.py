from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

class LLM:

    def __init__(self, groq_model: str, api_key: str):
        self.groq_model = groq_model
        self.api_key = api_key

    def get_llm(self):
        try:
            logger.info(f"Loading LLM: {self.groq_model}")
            
            llm = ChatGroq(model=self.groq_model, groq_api_key=self.api_key, temperature=0)
            
            logger.info("LLM loaded successfully.")
            return llm
        
        except Exception as e:
            logger.exception("Failed to load LLM.")
            raise CustomException(e)
        
        
        
    def prompt(self):
        try:
            logger.info("Creating Prompt Template")
            
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an AI Customer Support Agent.
                        Answer ONLY using the provided context.
                        If the answer cannot be found,
                        reply:
                        "I don't have enough information."
                        Context:
                        {context}
                        """
                    ),
                    (
                        "human",
                        "{question}"
                    )
                ]
            )
            return prompt
        
        except Exception as e:
            logger.exception("Failed to create prompt.")
            raise CustomException(e)
        
    