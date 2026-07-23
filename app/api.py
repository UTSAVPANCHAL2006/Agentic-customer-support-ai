from fastapi import FastAPI
from pydantic import BaseModel

from app.config.config import (
    GROQ_MODEL_NAME, GROQ_API_KEY, KB_DIR, RESOLVED_TICKETS_FILE, OUTPUT_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL,
    QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, VECTOR_SIZE,
)

from app.rag.llm import LLM
from app.rag.loader import Loader
from app.rag.chunk import Chunker
from app.rag.embedding import Embedding
from app.rag.qdrant import QdrantDB
from app.rag.retriever import Retriever
from app.rag.generate import Generator

from app.agents.graph import AgentGraph
from app.agents.tools.order_tool import OrderTool
from app.agents.tools.ticket_tool import TicketTool
from app.agents.tools.user_tool import UserTool

print("Loading LLM...")
llm = LLM(groq_model=GROQ_MODEL_NAME, api_key=GROQ_API_KEY).get_llm()

print("Loading Documents...")
loader = Loader(kb_path=KB_DIR, resolved_path=RESOLVED_TICKETS_FILE, output_path=OUTPUT_PATH)
docs = loader.load_all_documents()

chunker = Chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
chunks = chunker.create_text_chunks(docs)

embedding = Embedding(model_name=EMBEDDING_MODEL)
embedding_model = embedding.get_embedding()

qdrant = QdrantDB(
    qdrant_url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION,
    vector_size=VECTOR_SIZE,
    api_key=QDRANT_API_KEY,
)

if qdrant.collection_exists_with_data():
    print(f"Qdrant collection '{QDRANT_COLLECTION}' already populated. Skipping upload.")
else:
    print("First-time setup: uploading documents to Qdrant Cloud...")
    qdrant.create_collection()
    qdrant.upload_document(documents=chunks, embedding_model=embedding_model)
    print("Upload complete.")

retriever = Retriever(
    embedding_model=embedding_model,
    documents=chunks,
    qdrant_url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION,
    api_key=QDRANT_API_KEY,
)

generator = Generator(llm)
order_tool = OrderTool()
ticket_tool = TicketTool()
user_tool = UserTool()

print("Compiling Graph...")
graph = AgentGraph(
    retriever=retriever,
    generator=generator,
    classify=llm,
    llm=llm,
    order_tool=order_tool,
    ticket_tool=ticket_tool,
    user_tool=user_tool,
)

app = FastAPI()

# add rate limiting - max 20 requests per 60 seconds per ip
from app.middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

class ChatRequest(BaseModel):
    ticket: str
    thread_id: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    from fastapi.responses import StreamingResponse
    from app.prompts.generate_prompt import GENERATE_PROMPT
    from app.config.config import LANGFUSE_ENABLED
    
    callbacks = []
    if LANGFUSE_ENABLED:
        from langfuse.langchain import CallbackHandler
        langfuse_handler = CallbackHandler()
        callbacks.append(langfuse_handler)

    try:
        result = graph.run(ticket=request.ticket, thread_id=request.thread_id, callbacks=callbacks)

        action = result.get("action", "")
        
        if action == "blocked":
            def blocked_stream():
                yield result.get("response", "This request violates safety policies and has been blocked.")
            return StreamingResponse(blocked_stream(), media_type="text/plain")

        documents   = result.get("documents", [])
        tool_result = result.get("tool_result") or {}
        order_id    = result.get("order_id")
        ticket_id   = result.get("ticket_id")
        all_messages = result.get("messages", [])
        history = all_messages[:-2] if len(all_messages) >= 2 else []

        def token_stream():
            for chunk in generator.stream_generate(
                ticket=request.ticket,
                documents=documents,
                tool_result=tool_result,
                order_id=order_id,
                ticket_id=ticket_id,
                history=history
            ):
                yield chunk
        return StreamingResponse(token_stream(), media_type="text/plain")
    except Exception as e:
        import traceback
        error_msg = f"Internal Server Error details: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        def error_stream():
            yield error_msg
        return StreamingResponse(error_stream(), media_type="text/plain", status_code=500)
