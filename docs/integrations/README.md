# Integration adapters

This library is deliberately **integration-agnostic**: the per-form folder
is the contract, and adapters translate between it and a host system. None
of the adapters below are built yet — these are specifications so they can
be implemented independently and consistently.

Every adapter consumes the same three artifacts per form and nothing else:

| Artifact | Role in an adapter |
|---|---|
| `schema.json` | source of truth for widget ids, types, pages, rects |
| `mapping.json` | canonical fact-key → field_id (the integration boundary) |
| `form.yaml` | routing/metadata (category, court, source, automation tier) |

The **canonical fact object** is the lingua franca. Adapters map their
host's data into it; the engine (or any filler) maps it onto widgets via
`mapping.json`. Shape (informal):

```jsonc
{
  "matter":  { "docket_number", "court_county", "court_location",
               "court_type", "case_type", "filing_date" },
  "parties": { "plaintiff": {...}, "defendant": {...},
               "attorney": { "full_name", "bar_number", ... },
               "child_1": {...}, "child_2": {...} /* numbered minor children */ },
  "party":   { "full_name", "first_name", "middle_name", "last_name",
               "address", "city", "state", "zip",
               "phone", "email", "date_of_birth", "signature" },
  "facts":   { /* form-specific keys, e.g. oth_issue_summary */ }
}
```

`first_name`/`middle_name`/`last_name` support forms with split name boxes. An
adapter may supply them explicitly or just supply `full_name` — the reference
filler derives the parts from `full_name` when they aren't given.

`parties.child_1`, `child_2`, … are numbered minor-child roles (forms with
"Child #1 / Child #2" blocks); each carries the same attrs as any party.

`parties.other_party` is the role-neutral opponent for forms the filer signs as
either side (e.g. an eviction Request for Mediation: *"I am ( ) the defendant
(tenant) ( ) the plaintiff (landlord)"*). There, `party` is the filer and
`parties.other_party` is "the other party listed on the summons" — don't
hard-code such a field to `plaintiff`/`defendant`, since the filer's role isn't
fixed.

| Adapter | File | What it bridges |
|---|---|---|
| docassemble | `docassemble.md` | guided web interviews → filled PDF |
| LangChain / LangGraph | `langchain-langgraph.md` | each form as a tool / graph node |
| PandaDoc | `pandadoc.md` | form schema → PandaDoc template fields |
| Pi harness | `pi-harness.md` | local agent harness fill loop |
| MCP server | `mcp-server.md` | expose the library as MCP tools |

When you build one, keep the canonical fact object stable — that is what
lets a docassemble interview and a LangGraph node share the same mappings.
