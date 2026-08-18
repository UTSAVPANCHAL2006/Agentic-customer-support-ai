from app.agents.state import Agentstate
from app.prompts.entity_prompt import ENTITY_PROMPT
from app.schema.entity import EntitySchema
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


class EntityExtractorNode:
    
    def __init__(self, llm):
        self.llm = llm
        
    def entity_extractor_node(self, state: Agentstate):
        try:
            logger.info("EntityExtractorNode started")
            structured_llm = self.llm.with_structured_output(
                EntitySchema, method="json_schema"
            )

            chain = ENTITY_PROMPT | structured_llm

            result = chain.invoke({
                "ticket": state["ticket"],
                "history": state.get("messages", [])[-4:]
            })

            updates = {}
            if result.order_id:
                updates["order_id"] = result.order_id
            if result.ticket_id:
                updates["ticket_id"] = result.ticket_id
            if result.user_id:
                updates["user_id"] = result.user_id
                
            logger.info(f"EntityExtractorNode result: extracted {list(updates.keys())}")
            return updates
            
        except Exception as e:
            logger.error(f"Error in EntityExtractorNode: {str(e)}")
            raise CustomException(f"EntityExtractorNode Failed", e)
