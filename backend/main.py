from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from agents.legal_retriever import run as legal_run
from agents.doc_drafter import run as doc_run, detect_document_type, docx_to_pdf_bytes, extract_collected_fields

app = FastAPI(title="SakhiBot API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust if you deploy elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/response models
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
    document_type: str = ""
    next_question: str = ""
    is_emergency: bool = False
    detected_lang: str = "en"

class DocumentRequest(BaseModel):
    document_type: str
    history: list = []

# Root and health endpoints
@app.get("/")
def root():
    return {"message": "Welcome to SakhiBot API"}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "project": "SakhiBot",
        "agents": ["legal_retriever", "doc_drafter"]
    }

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Check if document drafting is needed
        doc_result = doc_run(req.message, req.history)

        if doc_result["needs_document"]:
            # Agent 2 (doc drafter) leads, but we still fetch legal sources if relevant
            legal_result = legal_run(req.message)
            return ChatResponse(
                answer=doc_result.get("message") or "I need some details to draft your document.",
                sources=legal_result.get("sources", []),
                document_ready=doc_result.get("document_ready", False),
                document_type=doc_result.get("document_type", ""),
                next_question=doc_result.get("next_question", ""),
                detected_lang=req.language
            )

        # Agent 1 handles normal legal queries
        legal_result = legal_run(req.message)
        return ChatResponse(
            answer=legal_result.get("answer", "I couldn’t find an answer."),
            sources=legal_result.get("sources", []),
            detected_lang=req.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")

# Document generation endpoint
@app.post("/api/document")
async def generate_document(req: DocumentRequest):
    try:
        fields = extract_collected_fields(req.history)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields extracted from history.")
        pdf_bytes = docx_to_pdf_bytes(req.document_type, fields)
        filename = f"sakhibot_{req.document_type}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {e}")
