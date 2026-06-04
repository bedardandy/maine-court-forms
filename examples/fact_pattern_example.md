# Worked example: fact pattern → filled form

A concrete pass through the `docs/agent-workflow.md` protocol.

## The fact pattern (what a user might say)

> "Help a client in Cumberland County who wants a divorce. They have two minor
> children. The client is Jane Q. Doe, the spouse is John R. Roe."

## 1. Route

```bash
$ python3 tools/find_forms.py "divorce with two minor children"
Top individual forms:
  FM-080   Family   Divorce with Minor Children
  ...
```

## 2. Understand the form

```bash
$ python3 tools/find_forms.py --json "..."        # or MCP get_form("FM-080")
# read forms/FM-080/SKILL.md   -> facts needed
# check forms/FM-080/mapping.json "status"  -> trust tier
```

## 3. Build the canonical fact object (`case.json`)

```json
{
  "matter": { "court_county": "Cumberland", "court_location": "Portland",
              "case_type": "family_matters", "filing_date": "2024-03-15" },
  "parties": {
    "plaintiff": { "full_name": "Jane Q. Doe", "address": "123 Main Street",
                   "city": "Portland", "state": "ME", "zip": "04101" },
    "defendant": { "full_name": "John R. Roe" },
    "child_1":   { "full_name": "Sam Doe",  "date_of_birth": "2015-04-10" },
    "child_2":   { "full_name": "Alex Doe", "date_of_birth": "2018-09-05" }
  },
  "party": { "full_name": "Jane Q. Doe", "signature": "Jane Q. Doe" },
  "facts": { "marriage_date": "2012-06-30", "grounds": "Irreconcilable Differences" }
}
```
Anything the fact pattern doesn't state (DOBs, addresses) is **left out**, not
invented — those become the "missing facts" you report back.

## 4–5. Fetch + fill

```bash
python3 tools/fetch_pdfs.py --forms FM-080
python3 -m engine.fill_via_mapping --form FM-080 --case case.json --out /tmp/out
```

## 6. Report

> Filled `FM-080` (Divorce with Minor Children) → `/tmp/out/FM-080.filled.pdf`.
> Mapping tier: *draft* — verify field placement. **Missing facts to collect:**
> children's dates of birth, the defendant's address, docket number. Not legal
> advice — review against the official form before filing.

Each form's bundled `examples/sample_case.json` is a ready canonical object you
can copy and adapt.
