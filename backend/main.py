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
    from orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    result = orchestrator.process(req.message, {"language": req.language})
    
    return ChatResponse(
        answer=result.get("answer", "No response generated"),
        sources=result.get("sources", []),
        resources=result.get("resources", []),
        safety_plan=result.get("safety_plan", []),
        document_ready=result.get("document_ready", False),
        is_emergency=result.get("is_emergency", False),
        detected_lang=req.language
    )