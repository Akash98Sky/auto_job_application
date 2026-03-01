from mem0 import Memory
from mem0.configs.base import MemoryConfig, LlmConfig, EmbedderConfig, RerankerConfig, VectorStoreConfig
from langchain_cohere import CohereEmbeddings
from pathlib import Path
from .logger_config import get_logger
from .config import KNOWLEDGE_BASE_DIR, MEM0_MODEL_NAME

logger = get_logger(__name__)

class KnowledgeBase:
    def __init__(self, data_dir: str = KNOWLEDGE_BASE_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Ensure GROQ_API_KEY is in the environment.
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "embedding_model_dims": 1024,
                }
            ),
            llm=LlmConfig(
                provider="groq",
                config={
                    "model": MEM0_MODEL_NAME
                }
            ),
            embedder=EmbedderConfig(
                provider="langchain",
                config={
                    "model": CohereEmbeddings(
                        model="embed-english-v3.0"
                    ) # type: ignore
                }
            ),
            reranker=RerankerConfig(
                provider="cohere",
                config={
                    "model": "rerank-english-v3.0"
                }
            )
        )
        self.memory = Memory(config=config)

    def load_from_directory(self):
        """Loads all text and markdown files from the data directory into mem0."""
        logger.info(f"Loading knowledge base from {self.data_dir}...")
        for file_path in self.data_dir.glob("*.*"):
            if file_path.suffix in [".txt", ".md"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Add document content to memory associated with the application context
                        self.memory.add(content, user_id="applicant", metadata={"source": file_path.name})
                        logger.info(f"Loaded: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path.name}: {e}")

    def query(self, question: str) -> str:
        """Retrieves and formats answers from the knowledge base based on the given question."""
        # Query memory and fetch relevant facts
        results = self.memory.search(question, user_id="applicant", limit=5)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Format the retrieved facts into a cohesive answer
        facts = "\n".join([f"- {res}" for res in results])
        return facts

if __name__ == "__main__":
    # Test the KnowledgeBase
    kb = KnowledgeBase()
    kb.load_from_directory()
    logger.info("Test Query: What are the applicant's main skills?")
    logger.info(kb.query("What are the applicant's main skills?"))
