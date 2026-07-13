import json
from app.config.config import TICKETS_PATH , RESOLVED_TICKETS_FILE
        
class TicketTool:
    
    def __init__(self):
        with open(TICKETS_PATH,"r") as f:
            self.tickets = json.load(f)
            
        with open(RESOLVED_TICKETS_FILE,"r") as f:
            self.resolved_tickets_list = json.load(f)
            # Convert list of resolved tickets to a dictionary keyed by ticket_id for easy lookup
            self.resolved_tickets = {t["ticket_id"]: t for t in self.resolved_tickets_list}
        
    def get_tickets(self, ticket_id: str):
        
        ticket = self.tickets.get(ticket_id)
        
        if ticket is None:
            # Fallback to check if it's a past resolved ticket
            resolved = self.resolved_tickets.get(ticket_id)
            if resolved:
                return {
                    "success": True,
                    "ticket": resolved,
                    "message": "This is a past resolved ticket."
                }
                
            return {
                "success" : False,
                "message" : "Ticket Not Found"
            }
            
        ticket_copy = ticket.copy()
        ticket_copy["ticket_id"] = ticket_id
        return {
            "success": True,
            "ticket": ticket_copy
        }
    
    def check_ticket_status(self,ticket_id: str):
        
        ticket = self.tickets.get(ticket_id)
        
        if ticket is None:
            # Fallback for resolved tickets
            resolved = self.resolved_tickets.get(ticket_id)
            if resolved:
                return {
                    "success": True,
                    "status": "resolved",
                    "ticket": resolved
                }
                
            return {
                "success": False,
                "message": "Ticket not found."
            }

        ticket_copy = ticket.copy()
        ticket_copy["ticket_id"] = ticket_id
        return {
            "success": True,
            "status": ticket["status"],
            "ticket": ticket_copy
        }
        
