from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PATH = "chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5

# ── model fallback chain ─────────────────────────────────────────────────────
# if first model hits rate limit, automatically tries next one
LLM_MODELS = [
    "llama-3.1-8b-instant",       # fast, low token cost — primary
    "gemma2-9b-it",                # Google Gemma — fallback 1
    "mixtral-8x7b-32768",          # Mixtral — fallback 2
    "llama-3.3-70b-versatile",     # large model — last resort
]

LLM_MODEL = LLM_MODELS[0]  # default, overridden by fallback logic