from app.agents.state import Agentstate

def router(state:Agentstate):
    
    action = state["action"]
    
    return action