from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import KB_DIR, RESOLVED_TICKETS_FILE, OUTPUT_PATH, CHUNK_SIZE, CHUNK_OVERLAP

from app.rag.loader import Loader

logger = get_logger(__name__)

class Chunker:

    def __init__(self, chunk_size: int, chunk_overlap: int):
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ],
        )

    def create_text_chunks(self, documents):
        try:
            
            if not documents:
                raise ValueError("No documents found for chunking.")
            
            logger.info(f"Splitting {len(documents)} documents into chunks...")
            
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Generated {len(chunks)} chunks.")
            
            return chunks
        
        except Exception as e:
            logger.exception("Failed to create document chunks.")
            raise CustomException(e)
        
if __name__ == "__main__":
    
    
    loader = Loader(kb_path=KB_DIR, resolved_path=RESOLVED_TICKETS_FILE, output_path=OUTPUT_PATH)
    documents = loader.load_all_documents()
    
    chunker = Chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = chunker.create_text_chunks(documents)
    
    print(f"Documents:{len(documents)}")
    print(f"Chunks:{len(chunks)}")
    
    print("-" * 60)
    print(chunks[0].page_content)
    
    print("-" * 60)
    print(chunks[0].metadata)