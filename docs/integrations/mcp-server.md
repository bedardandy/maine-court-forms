# MCP server adapter (spec — not built)

Expose the form library over the [Model Context Protocol](https://modelcontextprotocol.io)
so any MCP-capable client (Claude Code, Claude Desktop, other agents) can
search, inspect, and fill Maine court forms as native tools.

## Tools

| Tool | Input | Output |
|---|---|---|
| `search_forms` | `query: str` | ranked `form_id`s + titles (over `form.yaml`) |
| `get_form` | `form_id: str` | `form.yaml` + required fact-keys from `mapping.json` |
| `lint_case` | `facts: dict, form_id?` | preflight issues (`catalog/canonical_case.schema.json` contract + role-vocabulary suggestions) |
| `fill_form` | `form_id, facts: dict` | path/bytes of filled PDF |
| `audit_form` | `form_id, pdf` | audit findings (majors by field) |

## Resources

Expose each form folder as an MCP resource tree so a client can read the
PDF, schema, and SKILL.md directly:

```
maine-forms://AD-001/README.md
maine-forms://AD-001/schema.json
maine-forms://AD-001/AD-001.pdf
```

## Why MCP fits

- `search_forms` + `get_form` make the **fact requirements discoverable** —
  the agent learns exactly which canonical keys a form needs before asking
  the user anything.
- `SKILL.md` is already written for an agent reader; serve it verbatim as
  the tool/resource description.
- Stateless: each call is self-contained against a form folder, so the
  server can be a thin wrapper over `engine/` with no session state.

## Implementation note

Start read-only (`search_forms`, `get_form`, resources) — that alone makes
the whole library usable from any MCP client. Add `fill_form`/`audit_form`
once the engine packaging is settled.
