from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PATH = "chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3-8b-8192"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5