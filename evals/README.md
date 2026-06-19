# Evaluations (`evals/`)

These **evals** are distinct from `tests/`. `tests/` pin internal invariants
(field placement, schema drift, auto-stamp guards). `evals/` assert the
**product contract** an LLM or automation system relies on: that the documented
`route → understand → extract → preflight → fill → verify` flow
(`docs/agent-workflow.md`) actually chains and yields a *correct completed
form*.

Every eval names the **assumption** it tests, computes a **metric**, and
asserts a **pass bar** — so a red eval points at a falsified product claim, not
just a broken test.

## Running

```bash
python3 -m evals.run                 # flow + fill (deterministic, model-free)
python3 -m evals.run --all           # every layer (llm/vision gated, may skip)
python3 -m evals.run --layer flow --json report.json
pytest evals/                        # same evals via pytest
```

Layers `flow` and `fill` are deterministic and PDF-free (they reuse
`tests/helpers.py`); they run in CI. `llm` and `vision` are gated and skip by
default.

## Layers

| Layer | Assumption | Gate |
|-------|------------|------|
| **flow** | the 6 steps chain — each step's output is a valid input to the next | always (deterministic) |
| **fill** | completed-form content is stable, correct, and tier-honest | always (deterministic) |
| **guidance** | every field has correct fill-value guidance (type/required/conditional) | always (deterministic) |
| **logic** | if/then rules are valid, drift-free, and fire correctly | always (deterministic) |
| **llm** | an LLM extracts a preflight-clean, required-fact-complete case | offline scores goldens; live: `MCF_EVAL_LLM=1` |
| **vision** | values land in the visually-correct widget | `MCF_EVAL_VISION=1` (needs blank PDFs + model) |

### flow — logical-flow / contract integrity
- `test_routing_recall` — drives `tools/find_forms.py` with every smoke
  narrative; top-5 recall over *existing* expected forms (regression floor).
- `test_required_facts_resolvable` — every form's declared `facts.required`
  resolves to content in its own sample case and reaches the filled output.
- `test_form_id_contract` — every catalog/workflow/mapping id matches the
  strict `^[A-Z]+(?:-[A-Z0-9]+)+$` pattern; the pattern rejects traversal
  payloads (the audit's form_id security contract, testable today).
- `test_preflight_roundtrip` — every shipped sample case is preflight-clean for
  its form, and a seeded role typo is caught (the gate bites).

### fill — completed-form correctness
- `test_fill_golden` — corpus-scale regression oracle: the PDF-free fill of
  every form's sample case is diffed against a committed golden in
  `golden/<ID>.kv.json`. Today's-date fields are normalized to a `<TODAY:...>`
  token for determinism. Regenerate with `python3 -m evals.fill.gen_golden
  --all` and review the diff to adopt an intended change.
- `test_trust_tier_invariants` — contentful tiers fill content;
  `no-mappable-fields` forms stay empty; recipe-dispatched forms are contentful.
- `test_warning_controls` — positive + negative controls for every
  `constraints.json` / `computations.json`: contradictions fire, clean input
  stays silent (no false positives).
- `test_verify_fill` — (PDF-gated) the real `engine.verify_fill` confirms
  intended fields are `placed` in the written PDF; auto-skips offline.

### guidance — per-field fill-value guidance
Each form ships `fill_guidance.json` (built by `tools/derive_field_guidance.py`)
declaring, per field: `value_type` (person_name / county / currency / date(+
format) / time / address / zip / phone / email / docket / checkbox / signature
/ ...), `required`, and `conditional` (one-of choice groups from
constraints.json). The evals prove it is complete, in-vocabulary, drift-free,
and — via counter-assertions — that the declared type agrees with the value the
engine actually resolves (a `.zip` key must be typed `zip`, etc.).
- `test_field_guidance.py` — coverage, vocabulary, no-drift, type/mapping
  agreement, checkbox/signature/date-format rules, required & conditional
  agreement, and preflight type-warning wiring.
- `test_value_types.py` — adversarial validator tests: valid values across all
  accepted formats must pass (no false positives), clear cross-type swaps must
  be flagged.

Regenerate after a mapping/constraints change: `python3 -m
tools.derive_field_guidance --all` (or `python3 tools/derive_field_guidance.py
--all`), review, commit.

### logic — if/then fill logic
Each form ships `logic.json` (built by `tools/derive_logic.py` from authored +
derived rules) with cross-field rules — conditional-required, attachment /
companion-form triggers, value incompatibilities, value inferences — evaluated
by `tools/logic_engine.py` (warnings-only). See `docs/logic-rules.md`.
- `test_logic_engine.py` — the expression evaluator: every operator + malformed
  input never raises (total).
- `test_logic_rules.py` — artifact validity, no-drift, real form/field
  references, and positive+negative firing controls for the authored seed
  (PFA, family/support, eviction/money, criminal), plus preflight wiring.

Regenerate after editing a `logic.authored.json` / `workflows.json`: `python3
tools/derive_logic.py --all`, review, commit.

### llm — extraction fidelity
- `extraction_cases.json` — a reviewed golden canonical case per smoke
  narrative. Offline (`TestGoldenCasesAreSound`) proves the fixtures are sound:
  preflight-clean, required-fact coverage = 1.0, routing floor. Live
  (`TestLiveExtractionFidelity`, `MCF_EVAL_LLM=1`) scores a model's extraction
  against the goldens.
- `test_input_robustness` — adversarial/malformed input (null, lists, scalars,
  traversal `form_id`) must produce clean rejections, never crashes (the audit's
  "fuzz the MCP server" next-step; also exercises the `is_canonical` boundary).

### vision — semantic placement
- `test_placement_judge` — thin wrapper over `tests/opus_judge.py`; fills,
  renders, and judges a pinned form set for value-vs-label misplacement.
  Opt-in, token-costing.

## Findings surfaced on first run (2026-06-19)

The evals are not just regression gates; their first run measured the repo and
found two things, documented in `docs/audit-response.md`:

1. **14 phantom routing targets** — `tools/smoke/fact_patterns.json` lists
   `expect_forms` ids with no `forms/<ID>/` directory (locked in
   `KNOWN_PHANTOM_FORMS`; a *new* one fails).
2. **Deterministic routing recall ≈ 0.69** (top-5, over existing expected
   forms). `MIN_RECALL` is a floor at this baseline — raise it as routing
   improves.

## Maintaining goldens

`golden/*.kv.json` are committed and human-reviewable. After an intended
mapping/recipe change, run `python3 -m evals.fill.gen_golden --all`, review the
diff, and commit. An unexpected diff is a regression.
