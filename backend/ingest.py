import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from config import CHROMA_PATH, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from pathlib import Path

class DocumentIngester:
    def __init__(self):
        self.embed_model = SentenceTransformer(EMBED_MODEL)
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name="legal_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
    def chunk_text(self, text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap
            
        return chunks
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def ingest_document(self, pdf_path, doc_name):
        """Process single PDF and add to ChromaDB"""
        print(f"Processing {doc_name}...")
        
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        print(f"  → Extracted {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = self.embed_model.encode(chunks).tolist()
        
        # Prepare metadata
        ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": doc_name, "chunk_id": i} for i in range(len(chunks))]
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        print(f"  ✓ Added to database\n")
    
    def ingest_all(self):
        """Ingest all PDFs from docs folder"""
        docs_dir = Path("docs")
        
        if not docs_dir.exists():
            print("docs/ folder not found")
            return
        
        pdf_files = list(docs_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in docs/")
            print("Please add legal documents to backend/docs/")
            return
        
        print(f"Found {len(pdf_files)} PDF files\n")
        
        for pdf_path in pdf_files:
            doc_name = pdf_path.stem
            self.ingest_document(str(pdf_path), doc_name)
        
        print(f"Ingestion complete! Total documents in DB: {self.collection.count()}")

if __name__ == "__main__":
    ingester = DocumentIngester()
    ingester.ingest_all()
