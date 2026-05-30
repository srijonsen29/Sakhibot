import os
import json
import hashlib
import time

CACHE_DIR = "query_cache"
CACHE_TTL = 60 * 60 * 24 * 7  # 7 days in seconds

os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(query: str) -> str:
    """Generate a unique filename from the query."""
    normalized = query.strip().lower()
    return hashlib.md5(normalized.encode()).hexdigest()


def get(query: str) -> dict | None:
    """
    Returns cached result if it exists and is not expired.
    Returns None if not found or expired.
    """
    key = _cache_key(query)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            cached = json.load(f)

        # check expiry
        if time.time() - cached.get("timestamp", 0) > CACHE_TTL:
            os.remove(path)
            return None

        print(f"  [CACHE HIT] Returning cached answer for: {query[:50]}...")
        return cached["data"]

    except Exception:
        return None


def set(query: str, data: dict) -> None:
    """
    Saves result to cache.
    Strips document_bytes before caching (not serializable).
    """
    key = _cache_key(query)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    # remove non-serializable fields
    safe_data = {k: v for k, v in data.items() if k != "document_bytes"}

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.time(),
                "query": query,
                "data": safe_data
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [CACHE] Failed to save: {e}")


def clear() -> int:
    """Clears all cached entries. Returns count deleted."""
    count = 0
    for f in os.listdir(CACHE_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, f))
            count += 1
    print(f"  [CACHE] Cleared {count} entries.")
    return count


def stats() -> dict:
    """Returns cache statistics."""
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    total_size = sum(
        os.path.getsize(os.path.join(CACHE_DIR, f))
        for f in files
    ) / 1024
    return {
        "entries": len(files),
        "size_kb": round(total_size, 1)
    }