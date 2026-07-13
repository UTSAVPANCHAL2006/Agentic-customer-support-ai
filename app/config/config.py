import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "support-agent-data"

KB_DIR = DATA_DIR / "knowledge_base"

MOCK_DB_DIR = DATA_DIR / "mock_db"

EVAL_DIR = DATA_DIR / "eval"

RESOLVED_TICKETS_FILE = (
    KB_DIR
    / "past_tickets"
    / "resolved_tickets.json"
)

OUTPUT_PATH="artifacts/loaded_documents.json"

CHUNK_SIZE=500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

QDRANT_URL        = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY    = os.getenv("QDRANT_API_KEY", None)
QDRANT_COLLECTION = "customer_support"
VECTOR_SIZE       = 768

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


ORDERS_PATH = BASE_DIR / "support-agent-data" / "mock_db" / "orders.json"
TICKETS_PATH = BASE_DIR / "support-agent-data" / "mock_db" / "tickets.json"
USERS_PATH = BASE_DIR / "support-agent-data" / "mock_db" / "users.json"
TRACKING_PATH = BASE_DIR / "support-agent-data" / "mock_db" / "tracking.json"

