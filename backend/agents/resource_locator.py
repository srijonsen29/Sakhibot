import json
import os
from difflib import SequenceMatcher

# ── load resource database once ──────────────────────────────────────────────
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resources.json")

with open(_DB_PATH, "r", encoding="utf-8") as f:
    _DB = json.load(f)

print(f"Resource Locator ready. "
      f"OSCs: {len(_DB['one_stop_centres'])} | "
      f"Shelters: {len(_DB['shelter_homes'])} | "
      f"Legal Aid: {len(_DB['legal_aid_offices'])}")


# ── fuzzy string matcher ──────────────────────────────────────────────────────
def _similarity(a: str, b: str) -> float:
    """Returns similarity score 0.0 to 1.0 between two strings."""
    return SequenceMatcher(
        None,
        a.lower().strip(),
        b.lower().strip()
    ).ratio()


def _matches_location(entry: dict, district: str, state: str) -> float:
    """
    Returns a match score for how well the entry matches the location.
    Higher = better match.
    """
    score = 0.0

    if district:
        d_score = _similarity(entry.get("district", ""), district)
        score += d_score * 2.0   # district match weighted higher

    if state:
        s_score = _similarity(entry.get("state", ""), state)
        score += s_score * 1.0

    return score


# ── state name normaliser ─────────────────────────────────────────────────────
STATE_ALIASES = {
    "wb":           "West Bengal",
    "west bengal":  "West Bengal",
    "bengal":       "West Bengal",
    "mh":           "Maharashtra",
    "maharashtra":  "Maharashtra",
    "up":           "Uttar Pradesh",
    "uttar pradesh":"Uttar Pradesh",
    "mp":           "Madhya Pradesh",
    "madhya pradesh":"Madhya Pradesh",
    "tn":           "Tamil Nadu",
    "tamil nadu":   "Tamil Nadu",
    "ka":           "Karnataka",
    "karnataka":    "Karnataka",
    "ts":           "Telangana",
    "telangana":    "Telangana",
    "gj":           "Gujarat",
    "gujarat":      "Gujarat",
    "rj":           "Rajasthan",
    "rajasthan":    "Rajasthan",
    "br":           "Bihar",
    "bihar":        "Bihar",
    "dl":           "Delhi",
    "delhi":        "Delhi",
    "new delhi":    "Delhi",
    "kl":           "Kerala",
    "kerala":       "Kerala",
    "od":           "Odisha",
    "odisha":       "Odisha",
    "orissa":       "Odisha",
    "as":           "Assam",
    "assam":        "Assam",
    "pb":           "Punjab",
    "punjab":       "Punjab",
    "hr":           "Haryana",
    "haryana":      "Haryana",
    "jh":           "Jharkhand",
    "jharkhand":    "Jharkhand",
    "cg":           "Chhattisgarh",
    "chhattisgarh": "Chhattisgarh",
    "uk":           "Uttarakhand",
    "uttarakhand":  "Uttarakhand",
    "hp":           "Himachal Pradesh",
    "himachal":     "Himachal Pradesh",
    "ch":           "Chandigarh",
    "chandigarh":   "Chandigarh",
}


def _normalise_state(state: str) -> str:
    """Normalises common state name variations."""
    return STATE_ALIASES.get(state.lower().strip(), state.strip())


# ── main search functions ─────────────────────────────────────────────────────
def find_oscs(district: str, state: str, limit: int = 3) -> list[dict]:
    """Find nearest One Stop Centres by district and state."""
    state = _normalise_state(state) if state else ""
    scored = []
    for entry in _DB["one_stop_centres"]:
        score = _matches_location(entry, district, state)
        if score > 0.3:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


def find_shelters(district: str, state: str, limit: int = 2) -> list[dict]:
    """Find shelter homes by district and state."""
    state = _normalise_state(state) if state else ""
    scored = []
    for entry in _DB["shelter_homes"]:
        score = _matches_location(entry, district, state)
        if score > 0.3:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


def find_legal_aid(district: str, state: str, limit: int = 2) -> list[dict]:
    """Find legal aid offices by district and state."""
    state = _normalise_state(state) if state else ""
    scored = []
    for entry in _DB["legal_aid_offices"]:
        score = _matches_location(entry, district, state)
        if score > 0.3:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


def get_helplines() -> list[dict]:
    """Returns all national helplines — always included."""
    return _DB["national_helplines"]


def format_resource_card(entry: dict) -> dict:
    """Formats a resource entry for the frontend card."""
    return {
        "name":        entry.get("name", ""),
        "type":        entry.get("type", ""),
        "address":     entry.get("address", ""),
        "phone":       entry.get("phone", ""),
        "open_hours":  entry.get("open_hours", ""),
        "district":    entry.get("district", ""),
        "state":       entry.get("state", ""),
    }


# ── question detector ─────────────────────────────────────────────────────────
def needs_location(query: str) -> bool:
    """
    Returns True if the user's query is asking for resources near them.
    """
    keywords = [
        "near me", "nearby", "nearest", "where to go", "where can i go",
        "shelter", "shelter home", "osc", "one stop", "one stop centre",
        "legal aid", "free lawyer", "legal help near",
        "kahan jaye", "kahan jana", "kahan milega", "nearest centre",
        "help centre", "crisis centre", "refuge", "safe place",
        "police station near", "magistrate near", "court near",
        "where should i go", "where do i go", "help me find"
    ]
    query_lower = query.lower()
    return any(kw in query_lower for kw in keywords)

CITY_TO_STATE = {
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Delhi": "Delhi",
    "Kolkata": "West Bengal",
    "Howrah": "West Bengal",
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Bengaluru": "Karnataka",
    "Mysuru": "Karnataka",
    "Hyderabad": "Telangana",
    "Warangal": "Telangana",
    "Ahmedabad": "Gujarat",
    "Surat": "Gujarat",
    "Jaipur": "Rajasthan",
    "Jodhpur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Agra": "Uttar Pradesh",
    "Patna": "Bihar",
    "Muzaffarpur": "Bihar",
    "Bhopal": "Madhya Pradesh",
    "Indore": "Madhya Pradesh",
    "Bhubaneswar": "Odisha",
    "Guwahati": "Assam",
    "Chandigarh": "Chandigarh",
    "Thiruvananthapuram": "Kerala",
    "Kochi": "Kerala",
}

def extract_location_from_query(query: str) -> tuple[str, str]:
    """
    Tries to extract district and state from the query itself.
    Returns (district, state) — empty strings if not found.
    """
    import re
    query_lower = query.lower()

    # check state aliases first (longest alias first)
    found_state = ""
    for alias in sorted(STATE_ALIASES.keys(), key=len, reverse=True):
        if re.search(r"\b" + re.escape(alias) + r"\b", query_lower):
            found_state = STATE_ALIASES[alias]
            break

    # check for city/district names
    known_districts = [
        "mumbai", "pune", "nagpur", "delhi", "kolkata", "howrah",
        "chennai", "coimbatore", "bengaluru", "mysuru", "hyderabad",
        "warangal", "ahmedabad", "surat", "jaipur", "jodhpur",
        "lucknow", "kanpur", "agra", "patna", "muzaffarpur",
        "bhopal", "indore", "bhubaneswar", "guwahati", "chandigarh",
        "thiruvananthapuram", "kochi"
    ]
    found_district = ""
    for d in known_districts:
        if d in query_lower:
            found_district = d.title()
            if not found_state:
                found_state = CITY_TO_STATE.get(found_district, "")
            break

    return found_district, found_state

# ── main agent run function ───────────────────────────────────────────────────
def run(
    query: str,
    district: str = "",
    state: str = ""
) -> dict:
    """
    Full Agent 3 pipeline.

    Input:
        query:    user's message
        district: user's district (from conversation or query)
        state:    user's state (from conversation or query)

    Output: {
        needs_location:   bool,
        location_found:   bool,
        resources:        list of formatted resource cards,
        helplines:        list of national helplines,
        message:          str,
        asking_for:       str  (what we're asking the user)
    }
    """
    # try to extract location from query if not provided
    if not district and not state:
        district, state = extract_location_from_query(query)

    # check if this query needs resources at all
    resource_needed = needs_location(query)

    if not resource_needed and not district and not state:
        return {
            "needs_location":  False,
            "location_found":  False,
            "resources":       [],
            "helplines":       get_helplines(),
            "message":         "",
            "asking_for":      ""
        }

    # if we need resources but don't have location yet — ask for it
    if not district and not state:
        return {
            "needs_location":  True,
            "location_found":  False,
            "resources":       [],
            "helplines":       get_helplines(),
            "message":         (
                "I can find the nearest shelter, One Stop Centre, and legal aid "
                "office for you. Which district and state are you in right now?"
            ),
            "asking_for":      "location"
        }

    # normalise state
    state = _normalise_state(state) if state else state

    # fetch resources
    oscs        = find_oscs(district, state)
    shelters    = find_shelters(district, state)
    legal_aids  = find_legal_aid(district, state)
    helplines   = get_helplines()

    # combine all resources
    all_resources = []
    for r in oscs:
        all_resources.append(format_resource_card(r))
    for r in shelters:
        all_resources.append(format_resource_card(r))
    for r in legal_aids:
        all_resources.append(format_resource_card(r))

    location_label = f"{district}, {state}".strip(", ")

    if all_resources:
        message = (
            f"I found {len(all_resources)} resources near {location_label}. "
            f"One Stop Centres are government-run 24x7 facilities that provide "
            f"shelter, police help, medical aid, and legal assistance all in one place. "
            f"They are completely free."
        )
    else:
        # no exact match — return state-level or national resources
        state_oscs = [
            e for e in _DB["one_stop_centres"]
            if _similarity(e.get("state", ""), state) > 0.7
        ]
        for r in state_oscs[:3]:
            all_resources.append(format_resource_card(r))

        if all_resources:
            message = (
                f"I could not find resources in {district} specifically, "
                f"but here are the nearest resources in {state}. "
                f"Call 181 (Women's Helpline) right now for immediate guidance."
            )
        else:
            message = (
                f"I could not find specific resources in your area. "
                f"Please call 181 (Women's Helpline) immediately — "
                f"they will guide you to the nearest One Stop Centre."
            )

    return {
        "needs_location":  True,
        "location_found":  True,
        "resources":       all_resources,
        "helplines":       helplines[:4],   # top 4 helplines
        "message":         message,
        "asking_for":      ""
    }