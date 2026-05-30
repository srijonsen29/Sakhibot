# SakhiBot — Women's Legal Rights AI Assistant

> Aapka haq, aapki bhasha mein (Your rights, in your language)

An agentic, multilingual AI chatbot that helps Indian women know their legal rights — in Hindi, Bengali, Tamil, and more. Built as a Final Year Project.

---

## What it does

- Answers legal questions grounded in actual Indian law (no hallucination)
- Generates filled FIR drafts and complaint documents ready to print
- Finds nearest shelters, One Stop Centres, and helplines by district
- Builds a personalised step-by-step safety plan
- Supports voice input and text-to-speech in multiple Indian languages
- Emergency mode — instant SOS card with 181, 100, nearest shelter

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TailwindCSS |
| Backend | FastAPI (Python) |
| Agent Orchestration | LangGraph |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| LLM | Groq API — Llama 3 |
| Translation | deep-translator + langdetect |
| Document Generation | python-docx + reportlab |

---

## Project Structure

    sakhibot/
    ├── backend/
    │   ├── agents/
    │   │   ├── legal_retriever.py   
    │   │   ├── doc_drafter.py       
    │   │   ├── resource_locator.py  
    │   │   └── safety_planner.py    
    │   ├── data/
    │   │   └── resources.json       
    │   ├── docs/                    
    │   ├── templates/               
    │   ├── config.py
    │   ├── main.py                  
    │   ├── ingest.py                
    │   ├── orchestrator.py          
    │   └── translate.py             
    └── frontend/
        └── src/
            ├── components/
            │   ├── ChatWindow.jsx
            │   ├── MessageBubble.jsx
            │   ├── SourceCard.jsx
            │   ├── VoiceButton.jsx
            │   ├── LanguageSelector.jsx
            │   ├── InputBar.jsx
            │   └── EmergencyBanner.jsx
            ├── App.jsx
            └── api.js

---

## Setup & Run

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment variables
Create `backend/.env`:
GROQ_API_KEY=your_groq_key_here

---

## Build Progress

| Day | Task | Status |
|---|---|---|
| Day 1 | Project setup + GitHub + environment | ✅ Done |
| Day 2 | PDF ingestion + ChromaDB knowledge base | ✅ Done |
| Day 3 | Agent 1 — Legal Retriever | ✅ Done |
| Day 4 | Agent 2 — Document Drafter | ✅ Done |
| Day 5 | Agent 3 — Resource Locator | ✅ Done |
| Day 6 | Agent 4 + LangGraph Orchestrator | ✅ Done |
| Day 7 | Language layer + FastAPI + Emergency mode | ⏳ |
| Day 8 | React chat UI components | ⏳ |
| Day 9 | Connect frontend to backend | ⏳ |
| Day 10 | Polish + TTS + Deploy live | ⏳ |
| Day 11 | Report Chapters 1–3 | ⏳ |
| Day 12 | Report Chapters 4–6 | ⏳ |
| Day 13 | Slides + demo prep | ⏳ |
| Day 14 | Final testing + submission | ⏳ |

---

## Legal Knowledge Base

| Document | Source | Status |
|---|---|---|
| Domestic Violence Act 2005 | indiacode.nic.in | ✅ Day 2 |
| POSH Act 2013 | indiacode.nic.in | ✅ Day 2 |
| IPC Section 498A | indiacode.nic.in | ✅ Day 2 |
| Maternity Benefit Act | indiacode.nic.in | ✅ Day 2 |
| Dowry Prohibition Act | indiacode.nic.in | ✅ Day 2 |
| Equal Remuneration Act | indiacode.nic.in | ✅ Day 2 |
| CrPC Sections 41/46 | indiacode.nic.in | ✅ Day 2 |
| Constitution Art 14–21 | legislative.gov.in | ✅ Day 2 |

---

*Final Year Project — B.Tech Computer Science & Engineering (Data Science)*
*Built with React + FastAPI + LangGraph + ChromaDB + Groq*
