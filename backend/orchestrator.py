from groq import Groq
from agents.legal_retriever import LegalRetriever
from agents.doc_drafter import DocumentDrafter
from agents.resource_locator import ResourceLocator
from agents.safety_planner import SafetyPlanner
from config import GROQ_API_KEY, LLM_MODEL

class AgentOrchestrator:
    """LangGraph-style orchestrator that routes queries to appropriate agents"""
    
    def __init__(self):
        self.llm = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.legal_retriever = LegalRetriever()
        self.doc_drafter = DocumentDrafter()
        self.resource_locator = ResourceLocator()
        self.safety_planner = SafetyPlanner()
    
    def classify_intent(self, message: str):
        """Classify user intent to route to appropriate agent"""
        message_lower = message.lower()
        
        # Emergency detection
        emergency_keywords = ["emergency", "danger", "help", "urgent", "threat", "violence now"]
        if any(kw in message_lower for kw in emergency_keywords):
            return "emergency"
        
        # Document drafting
        doc_keywords = ["fir", "complaint", "draft", "letter", "document", "file case"]
        if any(kw in message_lower for kw in doc_keywords):
            return "document"
        
        # Resource finding
        resource_keywords = ["helpline", "shelter", "centre", "contact", "phone number", "where to go"]
        if any(kw in message_lower for kw in resource_keywords):
            return "resources"
        
        # Safety planning
        safety_keywords = ["safety plan", "what should i do", "steps", "how to protect", "escape plan"]
        if any(kw in message_lower for kw in safety_keywords):
            return "safety_plan"
        
        # Default to legal query
        return "legal_query"
    
    def process(self, message: str, context: dict = None):
        """Main orchestration logic"""
        intent = self.classify_intent(message)
        
        if intent == "emergency":
            return self._handle_emergency()
        
        elif intent == "document":
            return self._handle_document_request(message, context)
        
        elif intent == "resources":
            return self._handle_resource_request(message, context)
        
        elif intent == "safety_plan":
            return self._handle_safety_plan(message, context)
        
        else:  # legal_query
            return self._handle_legal_query(message)
    
    def _handle_emergency(self):
        """Emergency response"""
        emergency_plan = self.safety_planner.get_emergency_plan()
        emergency_card = self.resource_locator.format_emergency_card()
        
        return {
            "answer": "🚨 EMERGENCY MODE ACTIVATED\n\n" + emergency_card,
            "safety_plan": emergency_plan["immediate_actions"],
            "resources": self.resource_locator.get_emergency_contacts(),
            "is_emergency": True,
            "priority": "CRITICAL"
        }
    
    def _handle_legal_query(self, message: str):
        """Handle legal information queries"""
        # Retrieve relevant legal context
        retrieval_result = self.legal_retriever.retrieve(message)
        
        if retrieval_result.get("error"):
            return {
                "answer": "Knowledge base not ready. Please run ingest.py to load legal documents.",
                "sources": [],
                "error": retrieval_result["error"]
            }
        
        # Get context for LLM
        context = self.legal_retriever.get_context(message)
        
        # Generate answer using LLM
        if self.llm:
            answer = self._generate_llm_response(message, context)
        else:
            answer = "LLM not configured. Add GROQ_API_KEY to .env file."
        
        return {
            "answer": answer,
            "sources": retrieval_result["sources"],
            "chunks": retrieval_result["chunks"]
        }
    
    def _handle_document_request(self, message: str, context: dict):
        """Handle document drafting requests"""
        details = context or {}
        
        if "fir" in message.lower():
            doc = self.doc_drafter.draft_fir(details)
        else:
            doc = self.doc_drafter.draft_complaint(details)
        
        return {
            "answer": f"I've prepared a {doc['document_type']} draft for you. Please review and fill in the required details.",
            "document": doc["content"],
            "document_ready": True,
            "document_type": doc["document_type"]
        }
    
    def _handle_resource_request(self, message: str, context: dict):
        """Handle resource location requests"""
        city = context.get("city") if context else None
        resources = self.resource_locator.get_all_resources(city)
        
        answer = f"Here are the resources available"
        if city:
            answer += f" in {city}"
        answer += ":\n\n"
        
        return {
            "answer": answer,
            "resources": resources,
            "helplines": resources["helplines"]
        }
    
    def _handle_safety_plan(self, message: str, context: dict):
        """Handle safety planning requests"""
        situation = context.get("situation", "domestic_violence") if context else "domestic_violence"
        plan = self.safety_planner.create_plan(situation, context)
        
        return {
            "answer": f"I've created a personalized safety plan for your situation.",
            "safety_plan": plan["steps"],
            "priority": plan["priority"]
        }
    
    def _generate_llm_response(self, query: str, context: str):
        """Generate response using Groq LLM"""
        system_prompt = """You are SakhiBot, a legal rights assistant for Indian women.
        
Your role:
- Provide accurate legal information based on Indian law
- Be empathetic and supportive
- Use simple, clear language
- Never give personal opinions, only cite actual law
- If unsure, say so clearly

Answer based ONLY on the provided legal context. Do not make up information."""

        user_prompt = f"""{context}

QUESTION: {query}

Provide a clear, accurate answer based on the legal information above."""

        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
