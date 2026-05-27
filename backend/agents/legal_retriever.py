from sentence_transformers import SentenceTransformer
import chromadb
from config import CHROMA_PATH, EMBED_MODEL, TOP_K

class LegalRetriever:
    """Agent 1: Retrieves relevant legal information from ChromaDB"""
    
    def __init__(self):
        self.embed_model = SentenceTransformer(EMBED_MODEL)
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            self.collection = self.client.get_collection(name="legal_docs")
        except:
            self.collection = None
    
    def retrieve(self, query: str, k: int = TOP_K):
        """Retrieve top-k relevant legal chunks"""
        if not self.collection:
            return {
                "chunks": [],
                "sources": [],
                "error": "Knowledge base not initialized. Run ingest.py first."
            }
        
        # Generate query embedding
        query_embedding = self.embed_model.encode([query])[0].tolist()
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        chunks = []
        sources = []
        
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            chunks.append({
                "text": doc,
                "source": metadata['source'],
                "similarity": round(1 - distance, 3)
            })
            
            if metadata['source'] not in sources:
                sources.append(metadata['source'])
        
        return {
            "chunks": chunks,
            "sources": sources,
            "query": query
        }
    
    def get_context(self, query: str):
        """Get formatted context string for LLM"""
        result = self.retrieve(query)
        
        if result.get("error"):
            return result["error"]
        
        context = "RELEVANT LEGAL INFORMATION:\n\n"
        for i, chunk in enumerate(result["chunks"], 1):
            context += f"[{i}] Source: {chunk['source']}\n"
            context += f"{chunk['text']}\n\n"
        
        return context
