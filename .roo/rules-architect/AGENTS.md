# Project Architecture Rules (Non-Obvious Only)

- Browser automation uses `browser-use` library with custom Agent architecture
- Knowledge base uses `mem0` framework with Qdrant vector store, Cohere embeddings, and Cohere reranking
- Resume ranking uses specific LLM prompt template requiring "Resume ID" format
- Job application flow: extract job description → select resume → query knowledge base → fill application
- Error handling defaults to permissive mode (continue rather than fail) to avoid blocking job applications