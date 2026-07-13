from typing import Optional
from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    
    ticket_id : Optional[str] = Field(default=None,description="Ticket ID if present, otherwise null")
    order_id : Optional[str] = Field(default=None,description="Order ID or Tracking ID if present, otherwise null")
    user_id : Optional[str] = Field(default=None,description="User ID if present, otherwise nul")