from app.config.config import (
    KB_DIR, RESOLVED_TICKETS_FILE, OUTPUT_PATH, 
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, 
    QDRANT_URL, QDRANT_COLLECTION, VECTOR_SIZE,
    GROQ_MODEL_NAME, GROQ_API_KEY
)
from app.rag.loader import Loader
from app.rag.chunk import Chunker
from app.rag.embedding import Embedding
from app.rag.qdrant import QdrantDB
from app.rag.retriever import Retriever
from app.rag.llm import LLM
from app.rag.generate import Generate

def run_pipeline():
    print("--- 1. Loading Documents ---")
    loader = Loader(kb_path=KB_DIR, resolved_path=RESOLVED_TICKETS_FILE, output_path=OUTPUT_PATH)
    docs = loader.load_all_documents()
    
    print("--- 2. Chunking Documents ---")
    chunker = Chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = chunker.create_text_chunks(docs)
    
    print("--- 3. Initializing Embedding ---")
    embedding = Embedding(model_name=EMBEDDING_MODEL)
    embedding_model = embedding.get_embedding()
    
    # Optional: Upload documents to Qdrant if they are not there
    # qdrant = QdrantDB(qdrant_url=QDRANT_URL, collection_name=QDRANT_COLLECTION, vector_size=VECTOR_SIZE)
    # qdrant.create_collection()
    # qdrant.upload_document(documents=chunks, embedding_model=embedding_model)
    
    print("--- 4. Initializing Retriever ---")
    retriever = Retriever(
        embedding_model=embedding_model,
        documents=chunks,
        qdrant_url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION
    )
    
    print("--- 5. Initializing LLM and Prompt ---")
    llm_setup = LLM(groq_model=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)
    llm_instance = llm_setup.get_llm()
    prompt_template = llm_setup.prompt()
    
    generator = Generate(llm=llm_instance, prompt=prompt_template)
    
    # Test Query
    query = "What is update for order id ORD-2007 stuck in 'awaiting pickup' for 4 days"
    print(f"\n--- 6. Running Query: '{query}' ---")
    
    # Retrieval
    retrieved_docs = retriever.similarity_search(query)

    print(f"Retrieved {len(retrieved_docs)} documents.\n")

    for i, doc in enumerate(retrieved_docs, 1):
            print("=" * 80)
            print(f"Document {i}")
            print("Metadata:", doc.metadata)
            print(doc.page_content[:500])
    
    # Generation
    response = generator.generate(question=query, documents=retrieved_docs)
    
    print("\n================ FINAL AI ANSWER ================")
    print(response.content)
    print("=================================================")

if __name__ == "__main__":
    run_pipeline()
