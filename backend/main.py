from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SakhiBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    history: list = []

class ChatResponse(BaseModel):
    answer: str
    sources: list = []
    resources: list = []
    safety_plan: list = []
    document_ready: bool = False
    is_emergency: bool = False
    detected_lang: str = "en"

@app.get("/api/health")
def health():
    return {"status": "ok", "project": "SakhiBot"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return ChatResponse(
        answer="Backend connected. Full pipeline coming Day 3-7.",
        detected_lang=req.language
    )