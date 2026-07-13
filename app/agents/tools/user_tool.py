import json

from app.config.config import USERS_PATH
class UserTool:
    
    def __init__(self):
        with open(USERS_PATH,"r") as f:

            self.users = json.load(f)
        
    def get_user(self , user_id):
        
        user = self.users.get(user_id)
        
        if user is None:
            return {
                "success" : False,
                "message" : "User Not Found"
            }
            
        return {
            "success" : True,
            "message" : user
        }
        
    def get_use_mail(self,user_id):
        
        user = self.users.get(user_id)
        
        if user is None:
            return {
                "success" : False,
                "message" : "User Not Found"
            }
            
        return {
            "success" : True,
            "message" : user["email"]
        }