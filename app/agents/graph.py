from langgraph.graph import StateGraph , START , END
from app.agents.state import Agentstate
from app.agents.nodes.retriever_node import RetrieverNode
from app.agents.nodes.generater_node import Generatenode
from app.agents.nodes.classify_node import Classifynode
from app.agents.nodes.entity_node import EntityExtractorNode
from app.agents.nodes.tool_node import ToolNode
from app.agents.nodes.guard_node import GuardNode


from app.agents.router import router
from langgraph.checkpoint.redis import RedisSaver
from app.config.config import REDIS_URL
from langchain_core.messages import HumanMessage
import uuid



class AgentGraph:
    
    def __init__(self, retriever , generator , classify, llm, order_tool, ticket_tool,user_tool):
        
        self.graph_builder = StateGraph(Agentstate)
        
        self.graph_builder.add_node("guard",GuardNode().guard_node)
        self.graph_builder.add_node("retriever",RetrieverNode(retriever).retriever_node)
        self.graph_builder.add_node("generator",Generatenode(generator).generate_node)
        self.graph_builder.add_node("classify",Classifynode(classify).classify_node)
        self.graph_builder.add_node("entity_extractor",EntityExtractorNode(llm).entity_extractor_node)
        self.graph_builder.add_node("tool",ToolNode(order_tool, ticket_tool,user_tool).tool_node)

        self.graph_builder.add_edge(START,"guard")
        self.graph_builder.add_conditional_edges("guard", lambda state: state["action"], {"blocked": "generator", "": "classify"})
        self.graph_builder.add_edge("classify","entity_extractor")
        self.graph_builder.add_conditional_edges("entity_extractor",router,{"retrieve":"retriever","call_tool": "tool","clarify": "generator","escalate": "generator", "respond": "generator"})
        self.graph_builder.add_edge("retriever","generator")
        self.graph_builder.add_edge("tool","generator")
        self.graph_builder.add_edge("generator",END)

        
        # connect to redis and use it to save conversation memory
        memory = RedisSaver(REDIS_URL)
        memory.setup() # Automatically create missing RediSearch indexes
        self.graph = self.graph_builder.compile(checkpointer=memory)
        
        
      
    def run(self, ticket: str, thread_id: str = "default", callbacks=None):
        config = {"configurable": {"thread_id": thread_id}}
        if callbacks:
            config["callbacks"] = callbacks
            
        current_state = self.graph.get_state(config).values

        initial_state = {
            "ticket": ticket,
            "messages": [HumanMessage(content=ticket)], 
            "category": "",
            "urgency": "",
            "sentiment": "",
            "action": "",
            "tool_name": "",
            "documents": [],
            "tool_result": {},
            "response": "",
        }

        if not current_state:
            initial_state["order_id"] = None
            initial_state["ticket_id"] = None
            initial_state["user_id"] = None
        
        result = self.graph.invoke(initial_state, config=config)
        return result
    
    