from langchain_cohere import CohereEmbeddings
from mem0 import Memory
from mem0.configs.base import MemoryConfig, LlmConfig, EmbedderConfig, RerankerConfig, VectorStoreConfig
from pathlib import Path

from .base_agent import BaseAgent
from ..logger_config import get_logger
from ..config import KNOWLEDGE_BASE_DIR, MEM0_LLM_GROQ_MODEL, MEM0_EMBED_COHERE_MODEL, MEM0_RERANK_COHERE_MODEL

logger = get_logger(__name__)

class KnowledgeBaseAgent(BaseAgent):
    """
    Manages applicant personal profile data and knowledge base retrieval.
    Integrates mem0 framework with Qdrant vector database and Cohere embedding/reranking.

    Inherits:
        BaseAgent
    """

    def __init__(self, data_dir: str = KNOWLEDGE_BASE_DIR):
        """
        Initializes the KnowledgeBaseAgent with a specified data directory.

        Args:
            data_dir (str): Path to the folder containing knowledge base files.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        super().__init__()

        # Ensure isolated storage paths per agent instance to avoid database file locks
        qdrant_path = str(self.data_dir / "qdrant")
        history_db = str(self.data_dir / "memory_history.db")

        config = MemoryConfig(
            history_db_path=history_db,
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "embedding_model_dims": 1536,
                    "path": qdrant_path,
                }
            ),
            llm=LlmConfig(
                provider="groq",
                config={
                    "model": MEM0_LLM_GROQ_MODEL
                }
            ),
            embedder=EmbedderConfig(
                provider="langchain",
                config={
                    "model": CohereEmbeddings(
                        model=MEM0_EMBED_COHERE_MODEL
                    )
                }
            ),
            reranker=RerankerConfig(
                provider="cohere",
                config={
                    "model": MEM0_RERANK_COHERE_MODEL
                }
            )
        )
        self.memory = Memory(config=config)

    def load_from_directory(self) -> None:
        """
        Scans the configured data directory and loads all .txt and .md files
        into the mem0 memory storage, indexed under the user_id 'applicant'.

        Raises:
            IOError: If a file fails to open or read.
        """
        self.logger.info(f"Loading knowledge base documents from {self.data_dir}...")
        for file_path in self.data_dir.glob("*.*"):
            if file_path.suffix in [".txt", ".md"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Add document content to memory associated with the application context
                        self.memory.add(content, user_id="applicant", metadata={"source": file_path.name})
                        self.logger.info(f"Successfully loaded: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to load {file_path.name}: {e}")

    def query(self, question: str) -> str:
        """
        Queries the applicant's memory history and returns formatted facts.

        Args:
            question (str): A natural language question/query to search for.

        Returns:
            str: A newline-separated list of matching facts, or a default message
                 if no relevant details are found.
        """
        self.logger.info(f"Querying knowledge base: '{question}'")
        try:
            results = self.memory.search(question, user_id="applicant", limit=5)
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            # Format the retrieved facts into a cohesive answer
            facts = "\n".join([f"- {res}" for res in results])
            return facts
        except Exception as e:
            self.logger.error(f"Failed to query knowledge base: {e}")
            return "No relevant information found in the knowledge base."

    async def close(self) -> None:
        """
        Asynchronously closes active database resources and explicitly releases
        local Qdrant flock locks to permit concurrent execution and safe testing.
        """
        self.logger.info("Closing KnowledgeBaseAgent database connections...")
        try:
            if hasattr(self, "memory") and hasattr(self.memory, "vector_store"):
                vs = self.memory.vector_store
                if hasattr(vs, "client") and vs.client is not None:
                    client = vs.client
                    if hasattr(client, "_client") and client._client is not None:
                        local_client = client._client
                        if hasattr(local_client, "_flock_file") and local_client._flock_file is not None:
                            try:
                                import portalocker
                                portalocker.unlock(local_client._flock_file)
                            except Exception:
                                pass
                            local_client._flock_file.close()
                            local_client._flock_file = None
                            self.logger.debug("Released local Qdrant flock file lock successfully.")
                    if hasattr(client, "close"):
                        client.close()
        except Exception as e:
            self.logger.warning(f"Error while releasing Qdrant connection: {e}")
        await super().close()

if __name__ == "__main__":
    # Standard entry test
    import asyncio
    async def run_test():
        kb = KnowledgeBaseAgent()
        kb.load_from_directory()
        logger.info("Test Query: What are the applicant's main skills?")
        logger.info(kb.query("What are the applicant's main skills?"))
        await kb.close()
    asyncio.run(run_test())
