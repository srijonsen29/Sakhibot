import os
import io
import re
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_groq_client = Groq(api_key=GROQ_API_KEY)

# ── document type detector ───────────────────────────────────────────────────
def detect_document_type(query: str) -> str:
    query_lower = query.lower()

    fir_keywords = [
        "fir", "police complaint", "file complaint", "register case",
        "police station", "arrest", "498a", "beating", "assault"
    ]
    dv_keywords = [
        "domestic violence", "dv act", "protection order", "residence order",
        "husband violence", "magistrate", "court complaint", "dv complaint"
    ]
    posh_keywords = [
        "sexual harassment", "workplace harassment", "posh", "icc",
        "internal complaints", "internal committee", "office harassment",
        "employer harassment", "harassment at work", "complaint against boss",
        "boss harassing", "boss is harassing", "manager harassing",
        "supervisor harassment", "colleague harassment", "workplace abuse",
        "harassed at office", "harassed at workplace", "workplace sexual abuse"
    ]

    # FIR detection
    for kw in fir_keywords:
        if kw in query_lower:
            return "fir"

    # DV complaint detection (only if filing intent is clear)
    if any(kw in query_lower for kw in dv_keywords):
        if "file" in query_lower or "complaint" in query_lower or "draft" in query_lower:
            return "dv_complaint"
        else:
            return "none"  # let Agent 1 handle rights/definitions

    # POSH complaint detection
    for kw in posh_keywords:
        if kw in query_lower:
            return "posh_complaint"
        
    # Regex fallback for natural phrasing
    if re.search(r"(boss|manager|supervisor).+harass", query_lower):
        return "posh_complaint"

    return "none"


# ── conversational detail collector ─────────────────────────────────────────
def collect_details_prompt(document_type: str, history: list) -> str:
    required_fields = {
        "fir": [
            "complainant_name", "complainant_address", "complainant_phone",
            "accused_name", "incident_date", "incident_place",
            "incident_nature", "police_station",
        ],
        "dv_complaint": [
            "complainant_name", "complainant_address", "complainant_phone",
            "complainant_age", "accused_name", "accused_address",
            "relationship", "incident_date", "incident_nature", "court_district",
        ],
        "posh_complaint": [
            "complainant_name", "designation", "department", "complainant_phone",
            "accused_name", "accused_designation", "organization_name",
            "incident_date", "incident_place", "incident_nature",
        ],
    }

    questions = {
        "complainant_name":     "What is your full name?",
        "complainant_address":  "What is your current address?",
        "complainant_phone":    "What is your phone number?",
        "complainant_age":      "What is your age?",
        "accused_name":         "What is the full name of the person you are complaining against?",
        "accused_address":      "What is the address of the accused person?",
        "accused_designation":  "What is the designation/job title of the accused?",
        "accused_department":   "Which department does the accused work in?",
        "relationship":         "What is your relationship to the accused? (e.g. husband, in-law, colleague)",
        "incident_date":        "On what date did the incident occur? (e.g. 24 May 2026)",
        "incident_place":       "Where did the incident take place?",
        "incident_nature":      "Please briefly describe what happened. What did the accused do?",
        "police_station":       "Which police station is nearest to your location?",
        "court_district":       "Which district are you in? (for the court application)",
        "organization_name":    "What is the name of your organisation/company?",
        "designation":          "What is your job designation/title?",
        "department":           "Which department do you work in?",
        "state":                "Which state are you in?",
        "district":             "Which district are you in?",
    }

    fields = required_fields.get(document_type, [])
    collected = extract_collected_fields(history)

    for field in fields:
        if field not in collected:
            return questions.get(field, f"Please provide your {field}.")
    return ""


# ── field extractor ─────────────────────────────────────────────────────────
def extract_collected_fields(history: list) -> dict:
    if not history:
        return {}
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in history
        if isinstance(msg, dict) and "role" in msg and "content" in msg
    ])
    extraction_prompt = f"""Extract the following information from this conversation if mentioned.
Return ONLY a valid JSON object with the field names as keys.
If a field is not mentioned, do not include it.

Fields to extract:
complainant_name, complainant_address, complainant_phone, complainant_age,
accused_name, accused_address, accused_designation, accused_department,
relationship, incident_date, incident_place, incident_nature,
police_station, court_district, organization_name, designation,
department, state, district

Conversation:
{history_text}

Return only JSON, nothing else."""
    try:
        response = _groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0,
            max_tokens=512
        )
        raw = response.choices[0].message.content.strip()
        import json
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        if parsed:
            return parsed
    except Exception as e:
        print(f"Field extraction error: {e}")

    # 🔧 Fallback: parse system markers injected during tests
    fields = {}
    for msg in history:
        if msg.get("role") == "system" and ":" in msg.get("content", ""):
            key, val = msg["content"].split(":", 1)
            fields[key.strip()] = val.strip()
    return fields

# ── document filler ─────────────────────────────────────────────────────────
def fill_template(document_type: str, fields: dict) -> bytes:
    template_map = {
        "fir":           "templates/fir_template.docx",
        "dv_complaint":  "templates/dv_complaint.docx",
        "posh_complaint":"templates/posh_complaint.docx",
    }
    template_path = template_map.get(document_type)
    if not template_path or not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = Document(template_path)

    def replace_in_paragraph(para, fields):
        for key, value in fields.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in para.text:
                for run in para.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, str(value))

    for para in doc.paragraphs:
        replace_in_paragraph(para, fields)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    replace_in_paragraph(para, fields)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ── PDF converter ───────────────────────────────────────────────────────────
def docx_to_pdf_bytes(document_type: str, fields: dict) -> bytes:
    buffer = io.BytesIO()
    doc_titles = {
        "fir":           "FIRST INFORMATION REPORT",
        "dv_complaint":  "APPLICATION UNDER DV ACT 2005 - SECTION 12",
        "posh_complaint":"COMPLAINT UNDER POSH ACT 2013",
    }
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []

    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    # Title
    title_style = ParagraphStyle("title", parent=styles["Heading1"],
                                 fontSize=14, alignment=TA_CENTER,
                                 spaceAfter=20)
    story.append(Paragraph(doc_titles.get(document_type, "LEGAL DOCUMENT"), title_style))
    story.append(Spacer(1, 12))

    # Field labels
    field_labels = {
        "complainant_name": "Complainant Name",
        "complainant_address": "Address",
        "complainant_phone": "Phone",
        "complainant_age": "Age",
        "accused_name": "Accused Name",
        "accused_address": "Accused Address",
        "accused_designation": "Accused Designation",
        "relationship": "Relationship",
        "incident_date": "Date of Incident",
        "incident_place": "Place of Incident",
        "incident_nature": "Description",
        "police_station": "Police Station",
        "court_district": "Court District",
        "organization_name": "Organisation",
        "designation": "Your Designation",
        "department": "Department",
        "state": "State",
        "district": "District",
    }

    # Table of fields
    table_data = [["Field", "Details"]]
    for field, label in field_labels.items():
        if field in fields and fields[field]:
            table_data.append([label, str(fields[field])])

    if len(table_data) > 1:
        t = Table(table_data, colWidths=[180, 300])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F6E56")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FAF6")]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

    story.append(Spacer(1, 20))

    # Footer
    footer_style = ParagraphStyle(
        "footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666")
    )
    story.append(Paragraph(
        "Generated by SakhiBot — AI Legal Rights Assistant for Women in India",
        footer_style
    ))
    story.append(Paragraph(
        "This document is a draft. Please review with a lawyer before submission.",
        footer_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ── main agent run function ──────────────────────────────────────────────────
def run(query: str, history: list = []) -> dict:
    """
    Full Agent 2 pipeline.
    """
    # detect document type needed
    doc_type = detect_document_type(query)

    # check history for previously detected doc type
    if doc_type == "none":
        for msg in history:
            if isinstance(msg, dict) and msg.get("role") == "system":
                if "doc_type:" in msg.get("content", ""):
                    doc_type = msg["content"].split("doc_type:")[-1].strip()
                    break

    if doc_type == "none":
        return {
            "needs_document": False,
            "document_type": "none",
            "next_question": "",
            "document_ready": False,
            "document_bytes": None,
            "filename": "",
            "message": ""
        }

    # check what fields are still needed
    next_question = collect_details_prompt(doc_type, history)

    if next_question:
        return {
            "needs_document": True,
            "document_type": doc_type,
            "next_question": next_question,
            "document_ready": False,
            "document_bytes": None,
            "filename": "",
            "message": f"To prepare your {doc_type.replace('_', ' ')}, I need a few details.\n\n{next_question}"
        }

    # all details collected — generate document
    fields = extract_collected_fields(history)

    # add defaults for missing optional fields
    defaults = {
        "state": "India",
        "district": fields.get("court_district", "Your District"),
        "accused_address": "As known to complainant",
        "accused_department": "As applicable",
    }
    for k, v in defaults.items():
        if k not in fields:
            fields[k] = v

    try:
        pdf_bytes = docx_to_pdf_bytes(doc_type, fields)
        filename = f"sakhibot_{doc_type}_{fields.get('complainant_name', 'draft').replace(' ', '_')}.pdf"

        return {
            "needs_document": True,
            "document_type": doc_type,
            "next_question": "",
            "document_ready": True,
            "document_bytes": pdf_bytes,
            "filename": filename,
            "message": (
                f"Your {doc_type.replace('_', ' ')} is ready to download. "
                f"Please review it carefully and take it to the relevant authority. "
                f"Remember: Section 154 of CrPC requires police to register your FIR."
            )
        }
    except Exception as e:
        return {
            "needs_document": True,
            "document_type": doc_type,
            "next_question": "",
            "document_ready": False,
            "document_bytes": None,
            "filename": "",
            "message": f"There was an error generating your document: {str(e)}. Please try again."
        }
