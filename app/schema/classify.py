from typing import Literal
from pydantic import BaseModel, Field


class ClassificationSchema(BaseModel):
    
    category: str = Field(description=" Support category such as shipping, billing, return, account or general.")
    urgency: str = Field(description="Priority level: Low, Medium or High")
    sentiment: str = Field(description="Customer sentiment:Positive , Neutral or Angry")
    action: Literal["retrieve", "call_tool", "clarify", "escalate", "respond"] = Field(description="One of: retrieve, call_tool, clarify, escalate, or respond")
    tool_name: str = Field(description= "Operation to execute. "
            "Examples: track_order, cancel_order, "
            "check_return_eligibility, check_ticket_status, "
            "get_ticket, get_user, none.")