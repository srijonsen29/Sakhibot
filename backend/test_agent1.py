from agents.legal_retriever import run

from cache import stats as cache_stats, clear as cache_clear
print(f"Cache status: {cache_stats()}")

print("=" * 60)
print("SakhiBot — Agent 1 Test: Legal Retriever")
print("=" * 60)

# 20 test questions covering all 8 PDFs
test_questions = [
    # Domestic Violence Act
    "What is the definition of domestic violence under Indian law?",
    "Can a woman get a protection order against her husband?",
    "What is a residence order under the Domestic Violence Act?",
    "Who can file a domestic violence complaint?",

    # POSH Act
    "What is sexual harassment at workplace according to Indian law?",
    "How can a woman file a complaint against sexual harassment at office?",
    "What is an Internal Complaints Committee?",

    # IPC / CrPC
    "What is Section 498A of IPC?",
    "What is cruelty by husband or relatives under Indian law?",
    "Can police arrest a husband for beating his wife?",

    # Dowry
    "What is the punishment for dowry demand in India?",
    "What is the Dowry Prohibition Act?",

    # Maternity
    "How many weeks of maternity leave is a woman entitled to in India?",
    "What are maternity benefits for working women?",

    # Equal Remuneration
    "Can an employer pay a woman less than a man for the same work?",
    "What is equal remuneration for women in India?",

    # Constitution
    "What are the fundamental rights of women under the Constitution?",
    "What does Article 14 say about equality?",

    # Edge cases
    "What should a woman do if police refuse to register her FIR?",
    "What is the helpline number for women in distress in India?",
]

passed = 0
failed = 0

for i, question in enumerate(test_questions, 1):
    print(f"\n[{i}/20] Q: {question}")
    result = run(question)

    print(f"   Confidence : {result['confidence'].upper()}")
    print(f"   Sources    : {[s['source'] for s in result['sources'][:2]]}")
    print(f"   Answer     : {result['answer'][:180]}...")

    if result["confidence"] in ["high", "medium"]:
        passed += 1
        print("   Status     : PASS ✓")
    else:
        failed += 1
        print("   Status     : LOW CONFIDENCE ⚠")

print("\n" + "=" * 60)
print(f"Results: {passed}/20 passed | {failed}/20 low confidence")
print("=" * 60)

# interactive mode
print("\nEntering interactive mode. Type 'quit' to exit.\n")
while True:
    query = input("Ask a legal question: ").strip()
    if query.lower() == "quit":
        break
    if not query:
        continue
    result = run(query)
    print(f"\nAnswer     : {result['answer']}")
    print(f"Confidence : {result['confidence']}")
    print(f"Sources    : {[s['source'] for s in result['sources']]}\n")