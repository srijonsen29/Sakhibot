import os
from agents.doc_drafter import (
    detect_document_type,
    collect_details_prompt,
    extract_collected_fields,
    docx_to_pdf_bytes,
    run
)

print("=" * 60)
print("SakhiBot — Agent 2 Test: Document Drafter")
print("=" * 60)

# Test 1: document type detection
print("\n[TEST 1] Document type detection")
test_queries = [
    ("I want to file a police FIR against my husband",   "fir"),
    ("I need to file a domestic violence complaint",      "dv_complaint"),
    ("My boss is harassing me sexually at workplace",     "posh_complaint"),
    ("What are my rights under the DV Act?",             "none"),
    ("husband beating me I want to file complaint",       "fir"),
]
for query, expected in test_queries:
    result = detect_document_type(query)
    status = "PASS ✓" if result == expected else f"FAIL ✗ (got {result})"
    print(f"  {status} | '{query[:50]}...' → {result}")

# Test 2: FIR question flow simulation
print("\n[TEST 2] FIR question flow simulation")
history = []
doc_type = "fir"

# expected answers mapped to fields
fields_order = [
    "complainant_name",
    "complainant_address",
    "complainant_phone",
    "accused_name",
    "incident_date",
    "incident_place",
    "incident_nature",
    "police_station",
]
answers = [
    "Priya Sharma",
    "123 MG Road, Dharavi, Mumbai 400017",
    "9876543210",
    "Ramesh Sharma",
    "24 May 2026",
    "Our home at 123 MG Road",
    "My husband beat me with his hands and verbally abused me",
    "Dharavi Police Station",
]

for idx, field in enumerate(fields_order):
    question = collect_details_prompt(doc_type, history)
    if not question:
        print("  All details collected!")
        break
    print(f"  Bot asks: {question}")
    answer = answers[idx]
    print(f"  User says: {answer}")

    # append Q&A
    history.append({"role": "assistant", "content": question})
    history.append({"role": "user", "content": answer})

    # inject field:value marker for testing
    history.append({"role": "system", "content": f"{field}:{answer}"})

print("  All details collected!")

# Test 3: field extraction
print("\n[TEST 3] Field extraction from history")
fields = extract_collected_fields(history)
print(f"  Extracted {len(fields)} fields:")
for k, v in fields.items():
    print(f"    {k}: {v}")

# Test 4: PDF generation
print("\n[TEST 4] PDF generation")
if fields:
    try:
        pdf_bytes = docx_to_pdf_bytes("fir", fields)
        output_path = "test_fir_output.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  PDF generated: {output_path} ({size_kb:.1f} KB) PASS ✓")
        print(f"  Open this file to verify the content looks correct")
    except Exception as e:
        print(f"  PDF generation FAILED: {e}")
else:
    print("  Skipped — no fields extracted")

# Test 5: full run() pipeline
print("\n[TEST 5] Full run() pipeline")
result = run("I want to file an FIR against my husband for beating me", [])
print(f"  needs_document : {result['needs_document']}")
print(f"  document_type  : {result['document_type']}")
print(f"  next_question  : {result['next_question']}")
print(f"  message        : {result['message'][:80]}...")

print("\n[TEST 2B] DV complaint flow simulation")
history = []
doc_type = "dv_complaint"

fields_order = [
    "complainant_name",
    "complainant_address",
    "complainant_phone",
    "complainant_age",
    "accused_name",
    "accused_address",
    "relationship",
    "incident_date",
    "incident_nature",
    "court_district",
]
answers = [
    "Anita Roy",
    "45 Park Street, Kolkata",
    "9123456780",
    "32",
    "Rajesh Roy",
    "45 Park Street, Kolkata",
    "Husband",
    "20 May 2026",
    "He hit me and threatened me",
    "Kolkata District Court",
]

for idx, field in enumerate(fields_order):
    question = collect_details_prompt(doc_type, history)
    if not question:
        print("  All details collected!")
        break
    print(f"  Bot asks: {question}")
    answer = answers[idx]
    print(f"  User says: {answer}")
    history.append({"role": "assistant", "content": question})
    history.append({"role": "user", "content": answer})
    history.append({"role": "system", "content": f"{field}:{answer}"})

print("  All details collected!")

fields = extract_collected_fields(history)
print(f"  Extracted {len(fields)} fields: {fields}")
pdf_bytes = docx_to_pdf_bytes("dv_complaint", fields)
with open("test_dv_output.pdf", "wb") as f:
    f.write(pdf_bytes)
print("  DV complaint PDF generated ✓")

print("\n[TEST 2C] POSH complaint flow simulation")
history = []
doc_type = "posh_complaint"

fields_order = [
    "complainant_name",
    "designation",
    "department",
    "complainant_phone",
    "accused_name",
    "accused_designation",
    "organization_name",
    "incident_date",
    "incident_place",
    "incident_nature",
]
answers = [
    "Meera Singh",
    "Software Engineer",
    "IT Department",
    "9876543210",
    "Arun Kumar",
    "Team Lead",
    "TechCorp Pvt Ltd",
    "15 May 2026",
    "Office premises",
    "He made inappropriate comments and advances",
]

for idx, field in enumerate(fields_order):
    question = collect_details_prompt(doc_type, history)
    if not question:
        print("  All details collected!")
        break
    print(f"  Bot asks: {question}")
    answer = answers[idx]
    print(f"  User says: {answer}")
    history.append({"role": "assistant", "content": question})
    history.append({"role": "user", "content": answer})
    history.append({"role": "system", "content": f"{field}:{answer}"})

print("  All details collected!")

fields = extract_collected_fields(history)
print(f"  Extracted {len(fields)} fields: {fields}")
pdf_bytes = docx_to_pdf_bytes("posh_complaint", fields)
with open("test_posh_output.pdf", "wb") as f:
    f.write(pdf_bytes)
print("  POSH complaint PDF generated ✓")


print("\n" + "=" * 60)
print("Agent 2 tests complete.")
print("=" * 60)

