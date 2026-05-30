import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH, EMBED_MODEL, TOP_K
from cache import get as cache_get, set as cache_set
from groq_client import chat as groq_chat

# ── initialise clients ───────────────────────────────────────────────────────
print("Initialising Legal Retriever...")
_embed_model = SentenceTransformer(EMBED_MODEL)
_chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _chroma_client.get_collection("sakhibot_legal")
print(f"Legal Retriever ready. DB has {_collection.count()} chunks.")

QUERY_ROUTING = {
    "Domestic Violence Act 2005": [
        "domestic violence", "dv act", "protection order", "residence order",
        "shared household", "aggrieved", "protection officer", "monetary relief",
        "custody order", "section 12", "section 18", "section 19", "section 3",
        "husband beat", "husband violence", "pati maar", "ghar mein maar",
        "file dv", "dv complaint", "magistrate complaint"
    ],
    "POSH Act 2013": [
        "sexual harassment", "workplace harassment", "posh", "icc",
        "internal complaints", "internal committee", "office harassment",
        "employer harassment", "section 2", "section 4", "section 9",
        "unwelcome", "sexual favour", "hostile work", "file complaint office",
        "complaint against boss", "harassment at work"
    ],
    "Indian Penal Code": [
        "498a", "section 498", "cruelty husband", "ipc", "penal code",
        "criminal", "punishment husband", "husband relative cruelty",
        "section 354", "section 376", "assault woman", "criminal force",
        "hurt wife", "bodily harm"
    ],
    "Dowry Prohibition Act": [
        "dowry", "dowry demand", "dowry prohibition", "dahej",
        "bride burning", "section 3 dowry", "section 4 dowry",
        "property demand marriage", "valuables marriage"
    ],
    "Maternity Benefit Act": [
        "maternity", "maternity leave", "pregnancy leave", "nursing",
        "maternity benefit", "weeks leave", "delivery leave",
        "pregnant employee", "childbirth leave"
    ],
    "Equal Remuneration Act": [
        "equal pay", "equal remuneration", "same work pay",
        "gender pay gap", "pay discrimination", "section 4 remuneration",
        "less salary woman", "woman paid less"
    ],
    "Code of Criminal Procedure": [
        "fir", "police complaint", "arrest", "bail", "first information",
        "section 154", "refuse fir", "police refuse", "cognizable",
        "magistrate court", "register complaint police"
    ],
    "Constitution of India": [
        "fundamental rights", "article 14", "article 15", "article 21",
        "constitutional rights", "right to equality", "right to life",
        "article 19", "basic rights"
    ],
}


# ── system prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are SakhiBot, a legal rights assistant for women in India.

Your rules:
1. Answer ONLY using the provided context documents. Do not use outside knowledge.
2. Always cite which Act or section your answer comes from.
3. If the answer is truly not found in the context, respond with EXACTLY this phrase and nothing else: "NOT_FOUND_IN_KB"
4. Keep answers clear and simple — the user may have limited education.
5. Be empathetic and supportive. The user may be in a difficult situation.
6. Always end with one practical next step the user can take right now.
7. Never discourage the user from seeking help.
"""


def retrieve(query: str) -> dict:
    query_lower = query.lower()

    # routing check
    target_act = None
    for act, keywords in QUERY_ROUTING.items():
        if any(kw in query_lower for kw in keywords):
            target_act = act
            break

    query_embedding = _embed_model.encode([query]).tolist()

    if target_act:
        # restrict retrieval to that Act
        results = _collection.query(
            query_embeddings=query_embedding,
            n_results=TOP_K,
            where={"source": target_act}
        )
    else:
        # normal retrieval
        results = _collection.query(
            query_embeddings=query_embedding,
            n_results=TOP_K
        )

    chunks    = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0]  if results["metadatas"]  else []

    sources = []
    seen = set()
    for meta in metadatas:
        key = f"{meta['source']}_{meta['chunk_index']}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "source":      meta["source"],
                "filename":    meta["filename"],
                "chunk_index": meta["chunk_index"]
            })

    return {"chunks": chunks, "sources": sources, "query": query}



def generate_answer(query: str, chunks: list) -> str:
    if not chunks:
        return (
            "I could not find relevant information in my knowledge base. "
            "Please consult a lawyer or call 181 (Women's Helpline) for immediate help."
        )

    context = "\n\n---\n\n".join([
        f"Context {i+1}:\n{chunk}"
        for i, chunk in enumerate(chunks)
    ])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": (
            f"Context documents:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer based only on the context above."
        )}
    ]

    answer = groq_chat(messages, temperature=0.1, max_tokens=1024)

    # replace sentinel with friendly message
    if "NOT_FOUND_IN_KB" in answer:
        return (
            "I could not find this specific information in my knowledge base. "
            "Please consult a lawyer or call 181 (Women's Helpline) for help."
        )

    return answer


def score_confidence(answer: str, chunks: list) -> str:
    """
    Smarter confidence scoring.
    Only marks LOW if the answer is genuinely not found.
    """
    # only true not-found triggers low
    if "NOT_FOUND_IN_KB" in answer:
        return "low"

    # replace the sentinel with a friendly message
    # (handled in generate_answer below)

    if len(chunks) >= 3:
        return "high"
    if len(chunks) >= 1:
        return "medium"
    return "low"

def run(query: str) -> dict:
    """Full pipeline with caching + hybrid retrieval."""

    # ── hardcoded factual answers not in any PDF ──────────────────────────────
    HARDCODED = {
        "helpline": {
            "keywords": ["helpline", "helpline number", "women helpline",
                         "distress number", "emergency number women",
                         "181", "1091", "call for help"],
            "answer": (
                "Women's helplines in India:\n\n"
                "• 181 — Women's Helpline (24x7, free, all states)\n"
                "• 1091 — Women in Distress (Police)\n"
                "• 7827-170-170 — NCW Helpline\n"
                "• 100 — Police Emergency\n"
                "• 112 — National Emergency Number\n\n"
                "Practical next step: Save 181 in your phone right now. "
                "It is free, confidential, and available 24 hours."
            ),
            "sources": [{"source": "National Commission for Women",
                         "filename": "ncw_helplines", "chunk_index": 0}]
        }
    }

    # check hardcoded answers first
    query_lower = query.lower()
    for key, data in HARDCODED.items():
        if any(kw in query_lower for kw in data["keywords"]):
            return {
                "answer":     data["answer"],
                "sources":    data["sources"],
                "chunks":     [],
                "confidence": "high",
                "query":      query
            }

    # check cache
    cached = cache_get(query)
    if cached:
        return cached

    # normal pipeline
    retrieval  = retrieve(query)
    chunks     = retrieval["chunks"]
    sources    = retrieval["sources"]
    answer     = generate_answer(query, chunks)
    confidence = score_confidence(answer, chunks)

    result = {
        "answer":     answer,
        "sources":    sources,
        "chunks":     chunks,
        "confidence": confidence,
        "query":      query
    }

    cache_set(query, result)
    return result