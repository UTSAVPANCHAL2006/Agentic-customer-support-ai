from langchain_qdrant import QdrantVectorStore
from langchain_classic.retrievers import EnsembleRetriever

from app.rag.bm25 import BM25
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


class Retriever:

    def __init__(self, embedding_model, documents, qdrant_url: str, collection_name: str, api_key: str = None):
        try:
            vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=embedding_model,
                url=qdrant_url,
                api_key=api_key,
                collection_name=collection_name,
            )

            dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
            bm25_retriever = BM25().create_retriever(documents)

            self.retriever = EnsembleRetriever(
                retrievers=[dense_retriever, bm25_retriever],
                weights=[0.5, 0.5],
            )

            logger.info("Hybrid Retriever Initialized")

        except Exception as e:
            raise CustomException(e)

    def similarity_search(self, query):
        try:
            return self.retriever.invoke(query)
        except Exception as e:
            raise CustomException(e)