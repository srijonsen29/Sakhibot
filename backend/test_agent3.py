from agents.resource_locator import (
    run, find_oscs, find_shelters,
    find_legal_aid, get_helplines,
    needs_location, extract_location_from_query,
    _normalise_state
)

print("=" * 60)
print("SakhiBot — Agent 3 Test: Resource Locator")
print("=" * 60)

# test 1 — state normalisation
print("\n[TEST 1] State name normalisation")
tests = [
    ("wb", "West Bengal"),
    ("maharashtra", "Maharashtra"),
    ("up", "Uttar Pradesh"),
    ("delhi", "Delhi"),
    ("tn", "Tamil Nadu"),
]
for alias, expected in tests:
    result = _normalise_state(alias)
    status = "PASS ✓" if result == expected else f"FAIL ✗ got {result}"
    print(f"  {status} | '{alias}' → {result}")

# test 2 — location extraction from query
print("\n[TEST 2] Location extraction from query")
queries = [
    ("I need help near Mumbai",           "Mumbai", "Maharashtra"),
    ("shelter home in Delhi",             "Delhi",  "Delhi"),
    ("help centre in West Bengal",        "",       "West Bengal"),
    ("what is domestic violence",         "",       ""),
]
for query, exp_d, exp_s in queries:
    d, s = extract_location_from_query(query)
    status = "PASS ✓" if d == exp_d and s == exp_s else f"FAIL ✗ got ({d}, {s})"
    print(f"  {status} | '{query[:40]}' → ({d}, {s})")

# test 3 — needs_location detector
print("\n[TEST 3] Resource need detector")
queries = [
    ("where can I go for help",            True),
    ("nearest shelter home",               True),
    ("what is domestic violence",          False),
    ("I need a safe place near me",        True),
    ("how to file FIR",                    False),
]
for query, expected in queries:
    result = needs_location(query)
    status = "PASS ✓" if result == expected else f"FAIL ✗ got {result}"
    print(f"  {status} | '{query}'")

# test 4 — OSC search
print("\n[TEST 4] One Stop Centre search")
search_tests = [
    ("Mumbai",  "Maharashtra"),
    ("Delhi",   "Delhi"),
    ("Kolkata", "West Bengal"),
    ("Chennai", "Tamil Nadu"),
    ("Jaipur",  "Rajasthan"),
]
for district, state in search_tests:
    results = find_oscs(district, state)
    status = "PASS ✓" if results else "FAIL ✗ no results"
    names = [r["name"] for r in results]
    print(f"  {status} | {district}, {state} → {names}")

# test 5 — helplines
print("\n[TEST 5] National helplines")
helplines = get_helplines()
print(f"  Total helplines: {len(helplines)}")
for h in helplines[:4]:
    print(f"  {h['phone']:>15} — {h['name']}")

# test 6 — full run() pipeline
print("\n[TEST 6] Full run() pipeline")
run_tests = [
    {
        "query":    "I need a shelter near me",
        "district": "Mumbai",
        "state":    "Maharashtra",
        "expect_resources": True
    },
    {
        "query":    "where can I go for help in Delhi",
        "district": "",
        "state":    "",
        "expect_resources": True
    },
    {
        "query":    "what is my right under DV act",
        "district": "",
        "state":    "",
        "expect_resources": False
    },
    {
        "query":    "nearest osc",
        "district": "",
        "state":    "",
        "expect_resources": False   # no location given
    },
]
for t in run_tests:
    result = run(t["query"], t["district"], t["state"])
    has_resources = len(result["resources"]) > 0
    status = "PASS ✓" if has_resources == t["expect_resources"] else "FAIL ✗"
    print(f"  {status} | '{t['query'][:45]}'")
    print(f"         resources: {len(result['resources'])} | "
          f"location_found: {result['location_found']}")
    if result["message"]:
        print(f"         message: {result['message'][:70]}...")

print("\n" + "=" * 60)
print("Agent 3 tests complete.")
print("=" * 60)