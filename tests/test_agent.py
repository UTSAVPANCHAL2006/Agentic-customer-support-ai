from app.config.config import (
    GROQ_MODEL_NAME,
    GROQ_API_KEY,
    KB_DIR,
    RESOLVED_TICKETS_FILE,
    OUTPUT_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION,
)

from app.rag.llm import LLM
from app.rag.loader import Loader
from app.rag.chunk import Chunker
from app.rag.embedding import Embedding
from app.rag.retriever import Retriever
from app.rag.generate import Generator

from app.agents.graph import AgentGraph

from app.agents.tools.order_tool import OrderTool
from app.agents.tools.ticket_tool import TicketTool
from app.agents.tools.user_tool import UserTool


print("Loading LLM...")

llm = LLM(
    groq_model=GROQ_MODEL_NAME,
    api_key=GROQ_API_KEY
).get_llm()

print("Loading Documents...")

loader = Loader(
    kb_path=KB_DIR,
    resolved_path=RESOLVED_TICKETS_FILE,
    output_path=OUTPUT_PATH,
)

docs = loader.load_all_documents()

chunker = Chunker(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

chunks = chunker.create_text_chunks(docs)

embedding = Embedding(
    model_name=EMBEDDING_MODEL
)

embedding_model = embedding.get_embedding()

retriever = Retriever(
    embedding_model=embedding_model,
    documents=chunks,
    qdrant_url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION,
)

generator = Generator(llm)

order_tool = OrderTool()
ticket_tool = TicketTool()
user_tool = UserTool()

graph = AgentGraph(
    retriever=retriever,
    generator=generator,
    classify=llm,
    llm=llm,
    order_tool=order_tool,
    ticket_tool=ticket_tool,
    user_tool=user_tool,
)

while True:

    query = input("\nCustomer > ")

    if query.lower() == "exit":
        break

    result = graph.run(query)

    print("\n==============================")
    print("FINAL STATE")
    print("==============================")

    print(result)

    print("\n==============================")
    print("RESPONSE")
    print("==============================")

    print(result["response"])