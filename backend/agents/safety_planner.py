class SafetyPlanner:
    """Agent 4: Creates personalized safety plans"""
    
    def __init__(self):
        self.plan_templates = {
            "immediate_danger": [
                "Call 181 (Women Helpline) or 100 (Police) immediately",
                "Move to a safe location - neighbor's house, public place, or police station",
                "Do not return home alone if unsafe",
                "Inform trusted family member or friend about your situation",
                "Keep your phone charged and accessible"
            ],
            "domestic_violence": [
                "Document all incidents with dates, times, and details",
                "Take photos of injuries (if any) as evidence",
                "Keep important documents ready (ID, bank details, property papers)",
                "Identify safe places you can go to quickly",
                "Inform trusted neighbors or friends who can help",
                "Keep emergency numbers saved in your phone",
                "Pack an emergency bag with essentials (clothes, medicines, documents)",
                "Open a separate bank account if possible",
                "Consult with a lawyer about legal options"
            ],
            "workplace_harassment": [
                "Document all incidents in writing with dates and details",
                "Save any emails, messages, or evidence",
                "Report to Internal Complaints Committee (ICC) within 3 months",
                "Inform HR department in writing",
                "Seek support from trusted colleagues",
                "Consult with a lawyer if needed",
                "Know your rights under POSH Act 2013"
            ],
            "legal_action": [
                "Gather all evidence (photos, messages, medical reports, witnesses)",
                "Get medical examination done if injured",
                "File FIR at nearest police station",
                "Request copy of FIR for your records",
                "Consult with a lawyer for legal guidance",
                "Apply for protection order if needed",
                "Keep all legal documents organized",
                "Attend all court hearings"
            ]
        }
    
    def create_plan(self, situation: str, details: dict = None):
        """Generate personalized safety plan based on situation"""
        situation_key = situation.lower().replace(" ", "_")
        
        base_plan = self.plan_templates.get(
            situation_key,
            self.plan_templates["domestic_violence"]
        )
        
        plan = {
            "situation": situation,
            "steps": base_plan.copy(),
            "priority": self._assess_priority(situation),
            "immediate_actions": [],
            "short_term": [],
            "long_term": []
        }
        
        # Categorize steps by timeline
        if situation_key == "immediate_danger":
            plan["immediate_actions"] = base_plan
            plan["priority"] = "CRITICAL"
        else:
            plan["immediate_actions"] = base_plan[:3]
            plan["short_term"] = base_plan[3:6] if len(base_plan) > 3 else []
            plan["long_term"] = base_plan[6:] if len(base_plan) > 6 else []
        
        return plan
    
    def _assess_priority(self, situation: str):
        """Assess urgency level"""
        critical_keywords = ["immediate", "danger", "emergency", "threat", "violence"]
        
        if any(keyword in situation.lower() for keyword in critical_keywords):
            return "CRITICAL"
        elif "harassment" in situation.lower() or "workplace" in situation.lower():
            return "HIGH"
        else:
            return "MEDIUM"
    
    def add_custom_step(self, plan: dict, step: str, category: str = "short_term"):
        """Add custom step to existing plan"""
        if category in plan:
            plan[category].append(step)
        return plan
    
    def get_emergency_plan(self):
        """Get immediate emergency response plan"""
        return {
            "priority": "CRITICAL",
            "immediate_actions": [
                "🚨 Call 181 or 100 NOW",
                "🏃 Leave to safe location immediately",
                "📱 Inform trusted contact",
                "🏥 Seek medical help if injured",
                "👮 File police complaint"
            ],
            "helplines": {
                "Women Helpline": "181",
                "Police": "100",
                "NCW": "7827-170-170"
            }
        }
