# If/then fill logic (`logic.json`)

Beyond per-field value semantics (`docs/field-guidance.md`), each form ships
`forms/<ID>/logic.json`: **cross-field if/then rules** that fire as warnings
when a case meets a condition — conditional-required fields, attachment and
companion-form triggers, value incompatibilities, and value inferences.

Like constraints/computations, this layer is **warnings-only**: a firing rule
never blocks or alters a fill. It is evaluated by `tools/logic_engine.py` at
preflight/fill time and surfaced by MCP `get_form` (`logic`) and `lint_case` /
`fill_form` (as `logic-*` warnings).

> Not legal advice. Rules (including statute citations) are a machine aid to be
> verified against the official form and current law.

## Rule kinds

| kind | fires when… | carries |
|------|-------------|---------|
| `conditional_required` | `when` true AND a `then.require` path is absent | `missing` |
| `attachment` | `when` true | `then.attachment` (document) |
| `companion_form` | `when` true | `then.form` (+ `required`) |
| `incompatible` | `when` (the contradiction) is true | — |
| `value_inference` | `when` true | `then.suggest` |
| `note` | `when` true | — |

Each fired rule yields `{code:"logic", rule_id, kind, severity, message,
authority?, …}`.

## Expression language (`when`)

Deterministic, total (never raises). Operands are an expression, a
`{"var": <path>}`, a bare path string (in `present`/`absent`/`truthy`), or a
JSON literal. A path reads the canonical case (`facts.*`, `matter.*`,
`parties.*`, `party.*`) or a resolved widget value (`field:<field_id>`).

```jsonc
{"and": [ {"truthy": "facts.has_minor_children"},
          {"present": "parties.child_1"} ]}
{"==": [ {"var": "facts.relationship"}, "spouse" ]}
{">":  [ {"var": "facts.maximum_withholding_amount"},
         {"var": "facts.twenty_five_percent_amount"} ]}
{"matches": [ {"var": "facts.relationship_description"}, "neighbor|stranger" ]}
{"in": [ {"var": "matter.court_type"}, ["District Court", "Superior Court"] ]}
```
Operators: `and`/`or`/`not`, `==`/`!=`/`<`/`<=`/`>`/`>=` (numbers parsed
through `$`, `,`, `%`), `in`, `contains`, `matches` (regex, case-insensitive),
`present`/`absent`/`truthy`. Comparisons that hit missing or non-numeric data
are simply false — never an error. **In comparisons/`matches`/`in`, wrap a
field reference as `{"var": "..."}`; a bare string is a literal.**

## Where rules come from

`tools/derive_logic.py` writes `logic.json` = **authored rules + derived
rules**:

- **Authored** (`forms/<ID>/logic.authored.json`, hand-maintained, legally
  sourced) — merged ahead of derived rules; the deriver never overwrites them.
  Seeded for four high-value families:
  - **Protection orders** (PA-001): always-file PA-005; confidential address →
    PA-015; non-qualifying relationship → suggests Protection from Harassment
    (PA-009). *19-A M.R.S. §4002; 5 M.R.S. §3801.*
  - **Family + support** (FM-004, FM-040): minor children → FM-050 affidavit +
    FM-040 worksheet; adjusted income can't exceed gross income. *19-A M.R.S.
    §2001, §2006.*
  - **Eviction + money** (CV-287, MJ-007): debt-buyer must attach the debt
    agreement and an unbroken chain of title; garnishment capped at 25% of
    disposable earnings. *32 M.R.S. §11013(9), §11019; 14 M.R.S. §3127; 15
    U.S.C. §1673(a).*
  - **Criminal** (CR-004): a real-estate bail bond must identify the pledged
    property. *15 M.R.S. §1071.*
- **Derived** (corpus-wide, deterministic):
  - **workflow companions** from `catalog/workflows.json` (`required` /
    `condition` steps);
  - **attachment triggers** from fields whose id/label says "…is attached" /
    "exhibit";
  - **time inference** — a `value_type:time` field reading H:MM (1–6) without
    AM/PM almost certainly means PM (your "1:00 = PM" example).

## Validation

`evals/logic/` proves: the evaluator is correct and total
(`test_logic_engine.py`); every `logic.json` is valid, drift-free, and
references real forms/fields; and the authored rules fire on the right cases
and stay silent otherwise — positive + negative controls
(`test_logic_rules.py`). Run `python3 -m evals.run --layer logic`.

## Regenerating

After editing a `logic.authored.json`, `workflows.json`, or a form's fields:

```bash
python3 tools/derive_logic.py --all      # or --form CV-007 [--print]
```
Review the diff and commit; `evals/logic/test_logic_rules.py` fails on drift.
