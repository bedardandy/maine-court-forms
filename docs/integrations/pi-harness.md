# Pi / local agent harness adapter (spec — not built)

A thin adapter for driving fills from a local agent harness (e.g. a
self-hosted model loop, a Raspberry-Pi-class edge node, or any harness that
can call Python and shell). This is the lowest-dependency integration: no
SaaS, no web framework — just the form folder and a fact object.

## Contract

The harness provides a **fact-collection callback** and consumes a
**fill+audit result**:

```python
def fill_with_harness(form_id, ask) -> dict:
    """
    ask(field_key, prompt) -> value      # harness collects one fact
    returns {"pdf": path, "audit": {...}} # filled PDF + audit summary
    """
    mapping = load("forms/%s/mapping.json" % form_id)
    facts = {}
    for field_id, key in mapping["map"].items():
        if key.endswith("()"):       # computed (today(), etc.)
            continue
        facts[key] = ask(key, f"Value for {key} ({field_id})?")
    return engine.fill_and_audit(form_id, facts)
```

## Why this maps cleanly to a small harness

- **No network needed.** Everything required to fill a form is in its
  folder; the only external call is to a local model for fact extraction or
  the optional vision audit.
- **Local vision audit fits the edge story.** The engine's audit can run
  against a locally-served vision model (the reference engine already
  supports an OpenAI-compatible endpoint), so a Pi-class node + a LAN GPU
  box can do the full fill→flatten→audit→repair loop offline.
- **Batch mode.** Point the harness at a directory of fact JSONs and a form
  list; it fills each and writes an audit ledger — useful for overnight
  self-improvement runs.

## Recommended loop

```
for case in cases:
    form_id = route(case)                    # form.yaml retriever
    res = fill_with_harness(form_id, ask)
    if res["audit"]["majors"]:               # truncation / blank / overlap
        repair(case, res["audit"])           # adjust facts, refill
```

## Open questions

- Where the harness stores per-form fact templates (suggest
  `examples/sample_case.json` as the seed schema).
- Whether to call recipe forms directly (preferred) or fall back to the
  generic schema filler when no recipe exists.
