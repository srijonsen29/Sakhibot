from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from agents.legal_retriever import run as legal_run
from agents.doc_drafter import run as doc_run, detect_document_type
from agents.resource_locator import run as resource_run

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
    district: str = ""
    state: str = ""

class ChatResponse(BaseModel):
    answer: str
    sources: list = []
    resources: list = []
    helplines: list = []
    safety_plan: list = []
    document_ready: bool = False
    document_type: str = ""
    next_question: str = ""
    is_emergency: bool = False
    detected_lang: str = "en"
    asking_for_location: bool = False

class DocumentRequest(BaseModel):
    document_type: str
    history: list = []

@app.get("/")
def root():
    return {"message": "Welcome to SakhiBot API"}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "project": "SakhiBot",
        "agents": ["legal_retriever", "doc_drafter", "resource_locator"]
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # agent 3 — resource locator
    resource_result = resource_run(
        req.message,
        district=req.district,
        state=req.state
    )

    # agent 2 — document drafter
    doc_result = doc_run(req.message, req.history)

    # agent 1 — legal retriever (always runs)
    legal_result = legal_run(req.message)

    # compose response
    answer = legal_result["answer"]
    if doc_result["needs_document"] and doc_result["message"]:
        answer = doc_result["message"]
    if resource_result["asking_for"] == "location":
        answer = resource_result["message"] + "\n\n" + answer

    return ChatResponse(
        answer=answer,
        sources=legal_result["sources"],
        resources=resource_result["resources"],
        helplines=resource_result["helplines"],
        document_ready=doc_result["document_ready"],
        document_type=doc_result["document_type"],
        next_question=doc_result["next_question"],
        detected_lang=req.language,
        asking_for_location=resource_result["asking_for"] == "location"
    )

@app.post("/api/document")
async def generate_document(req: DocumentRequest):
    from agents.doc_drafter import docx_to_pdf_bytes, extract_collected_fields
    fields = extract_collected_fields(req.history)
    pdf_bytes = docx_to_pdf_bytes(req.document_type, fields)
    filename = f"sakhibot_{req.document_type}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )