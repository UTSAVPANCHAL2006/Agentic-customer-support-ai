import os
import json

from pathlib import Path
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from langchain_community.document_loaders import DirectoryLoader , TextLoader
from langchain_core.documents import Document

logger = get_logger(__name__)

class Loader:
    
    def __init__(self, kb_path: str, resolved_path: str, output_path: str):
        self.kb_path = kb_path
        self.resolved_path = resolved_path
        self.output_path = output_path
        
    def load_documents(self):        
        try:
            
            logger.info(f"Loading MarkDown Documents From {self.kb_path}")
            
            loader =  DirectoryLoader(
                
                path=str(self.kb_path),
                glob="*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding":"utf-8"}
            )
            
            docs = loader.load()
            
            for doc in docs:
                doc.metadata["type"] = "policy"
                doc.metadata["source"] = Path(doc.metadata["source"]).name
                
            
            logger.info(f"Loaded {len(docs)} markdown documents.")
                
            return docs
        
        except Exception as e:
            logger.error("Error To Load MarkDown Data")
            raise CustomException("Failed To Load Data") from e
        
    def load_resolved_tickets(self):
        try :
            
            logger.info(f"Loading The Resolved Data {self.resolved_path}")
            
            with open(self.resolved_path, "r", encoding="utf-8") as file:
                tickets = json.load(file)
            
            documents = []
            
            for ticket in tickets:
                
                content = (
                    f"Ticket ID: {ticket['ticket_id']}\n"
                    f"Order ID: {ticket['order_id']}\n"
                    f"Category: {ticket['category']}\n"
                    f"Urgency: {ticket['urgency']}\n"
                    f"Sentiment: {ticket['sentiment']}\n"
                    f"Tags: {', '.join(ticket['tags'])}\n"
                    f"Issue: {ticket['issue']}\n\n"
                    f"Resolution: {ticket['resolution']}"
                )
                
                document = Document(
                    page_content=content,
                    metadata={
                        "source": "resolved_tickets.json",
                        "type": "resolved_ticket",
                        "ticket_id": ticket["ticket_id"],
                        "order_id": ticket["order_id"],
                        "category": ticket["category"],
                        "urgency": ticket["urgency"],
                        "sentiment": ticket["sentiment"],
                        "tags": ticket["tags"],
                    }
                )
                
                documents.append(document)

            logger.info(f"Loaded {len(documents)} resolved tickets.")

            return documents

        except Exception as e:
            logger.error("Failed to load resolved tickets.")
            raise CustomException(e)
        
    def load_all_documents(self):
        try:
            
            policy_docs = self.load_documents()
            
            ticket_docs = self.load_resolved_tickets()
            
            all_docs = policy_docs + ticket_docs
            
            logger.info(f"Total documents loaded: {len(all_docs)}")
            
            return all_docs
        
        except Exception as e:
            logger.error("Failed to load all documents.")
            raise CustomException(e)
                
    def save_documents(self, all_docs):
        try:
            
            output_path = Path(self.output_path)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            documents = []
            
            for doc in all_docs:
                documents.append(
                    {
                        "page_content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                )
                
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(documents, file, indent=4, ensure_ascii=False)
                
            logger.info(f"Saved {len(documents)} documents to {output_path}")
            
        except Exception as e:
            logger.error("Failed to save loaded documents.")
            raise CustomException(e)

if __name__ == "__main__":
    from app.config.config import KB_DIR , RESOLVED_TICKETS_FILE , OUTPUT_PATH
    
    loader = Loader(kb_path=KB_DIR, resolved_path=RESOLVED_TICKETS_FILE, output_path=OUTPUT_PATH)
    all_docs = loader.load_all_documents()
    print(f"Total Documents : {len(all_docs)}")
    loader.save_documents(all_docs)
    print("Documents saved successfully.")