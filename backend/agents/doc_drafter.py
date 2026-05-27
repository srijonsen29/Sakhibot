from datetime import datetime
from pathlib import Path

class DocumentDrafter:
    """Agent 2: Generates FIR drafts and complaint letters"""
    
    def __init__(self):
        self.templates_dir = Path("templates")
    
    def draft_fir(self, details: dict):
        """Generate FIR draft from user details"""
        template_path = self.templates_dir / "fir_template.txt"
        
        if not template_path.exists():
            return {"error": "FIR template not found"}
        
        template = template_path.read_text(encoding='utf-8')
        
        # Fill template with provided details
        fir_text = template.format(
            complainant_name=details.get('name', '[Your Name]'),
            age=details.get('age', '[Your Age]'),
            address=details.get('address', '[Your Address]'),
            incident_date=details.get('incident_date', '[Date of Incident]'),
            incident_time=details.get('incident_time', '[Time of Incident]'),
            incident_place=details.get('incident_place', '[Place of Incident]'),
            incident_description=details.get('description', '[Describe the incident in detail]'),
            accused_name=details.get('accused_name', '[Name of Accused]'),
            relationship=details.get('relationship', '[Relationship with Accused]'),
            accused_address=details.get('accused_address', '[Address of Accused]'),
            applicable_sections=details.get('sections', '[Relevant IPC Sections]'),
            witnesses=details.get('witnesses', '[Witness details if any]'),
            current_date=datetime.now().strftime('%d-%m-%Y'),
            contact_number=details.get('contact', '[Your Contact Number]'),
            police_station=details.get('police_station', '[Police Station Name]'),
            district=details.get('district', '[District]'),
            state=details.get('state', '[State]')
        )
        
        return {
            "document_type": "FIR",
            "content": fir_text,
            "ready": True
        }
    
    def draft_complaint(self, details: dict):
        """Generate complaint letter from user details"""
        template_path = self.templates_dir / "complaint_template.txt"
        
        if not template_path.exists():
            return {"error": "Complaint template not found"}
        
        template = template_path.read_text(encoding='utf-8')
        
        complaint_text = template.format(
            complaint_type=details.get('complaint_type', 'GENERAL COMPLAINT'),
            authority_name=details.get('authority', '[Authority Name]'),
            authority_address=details.get('authority_address', '[Authority Address]'),
            current_date=datetime.now().strftime('%d-%m-%Y'),
            subject=details.get('subject', '[Subject of Complaint]'),
            complainant_name=details.get('name', '[Your Name]'),
            age=details.get('age', '[Your Age]'),
            occupation=details.get('occupation', '[Your Occupation]'),
            workplace=details.get('workplace', '[Your Workplace]'),
            address=details.get('address', '[Your Address]'),
            complaint_description=details.get('description', '[Detailed description of complaint]'),
            incident_date=details.get('incident_date', '[Date of Incident]'),
            incident_location=details.get('incident_location', '[Location of Incident]'),
            persons_involved=details.get('persons_involved', '[Names and details of persons involved]'),
            evidence_details=details.get('evidence', '[Evidence or witness details]'),
            relief_requested=details.get('relief', '[What action you want taken]'),
            contact_number=details.get('contact', '[Your Contact Number]'),
            email=details.get('email', '[Your Email]'),
            enclosures=details.get('enclosures', '[List of attached documents]')
        )
        
        return {
            "document_type": "COMPLAINT",
            "content": complaint_text,
            "ready": True
        }
    
    def suggest_sections(self, case_type: str):
        """Suggest relevant IPC sections based on case type"""
        sections_map = {
            "domestic_violence": "IPC Section 498A (Cruelty by husband), Protection of Women from Domestic Violence Act 2005",
            "dowry": "IPC Section 304B (Dowry death), Dowry Prohibition Act 1961",
            "workplace_harassment": "Sexual Harassment of Women at Workplace Act 2013 (POSH Act)",
            "assault": "IPC Section 354 (Assault or criminal force to woman with intent to outrage her modesty)",
            "rape": "IPC Section 376 (Punishment for rape)",
            "stalking": "IPC Section 354D (Stalking)",
            "acid_attack": "IPC Section 326A (Acid attack)"
        }
        
        return sections_map.get(case_type.lower(), "Consult with legal expert for applicable sections")
