# LangChain / LangGraph adapter (spec — not built)

Expose each form as a **tool** (LangChain) or a **node** (LangGraph) so an
agent can select a form, collect facts conversationally, and emit a filled
PDF.

## LangChain tool shape

One dynamically-generated `StructuredTool` per form, or a single
`fill_maine_form` tool parameterized by `form_id`:

```python
class FillMaineForm(BaseModel):
    form_id: str            # e.g. "AD-001"
    facts: dict             # canonical fact object (see integrations/README)

def fill_maine_form(form_id: str, facts: dict) -> str:
    """Returns path to filled PDF."""
    # 1. load forms/<form_id>/mapping.json + schema.json
    # 2. resolve facts -> {field_id: value} via mapping
    # 3. hand to engine.form_filler (or recipe if automation_status==recipe)
```

The tool **description** for the agent is built from `form.yaml`
(`title`, `category`, `purpose`) so the model can route to the right form.
A retriever over all `form.yaml` files lets the agent search by need
("form to change a child's name") before committing to a `form_id`.

## LangGraph topology

```
[intake] -> [classify form] -> [collect facts loop] -> [fill] -> [audit] -> [END]
                                      ^                            |
                                      +-------- missing fields ----+
```

- **classify form**: vector search over `form.yaml` summaries → candidate
  `form_id`s.
- **collect facts loop**: compare required keys (from `mapping.json`)
  against state; ask the user for any missing. This is where the
  canonical fact object shines — it is the graph's shared state slice.
- **fill**: engine call.
- **audit**: optional — call the vision audit (engine) and route
  `truncated`/`blank_required` findings back into the collect loop.

## What the library already gives you

- Stable per-form tool schemas (no per-form Python needed — generate from
  `mapping.json`).
- The audit loop is a real, tested feedback edge, not a stub — the engine's
  consensus audit can score a fill and surface specific field issues.
