# Response to the 2026-06-19 security & code audit

This document (1) records a per-finding verdict on the external audit and
(2) describes the evaluation suite (`evals/`) added in response to the audit's
testing-gap findings — evals that test the repo's assumptions and prove the
logical flow of completed forms for LLM / automation consumers.

> The audit was performed against a separate working copy. Its headline metrics
> ("113 passing / 3744 subtests") describe *that* copy; none of its findings'
> code (e.g. `tools/form_id.py`, `SECURITY.md`) is present on this branch. The
> verdicts below are advisory — adopting the fixes is a separate change set.
> This branch's new work is the `evals/` suite (Part B).

## Part A — Verdict on each finding

| # | Finding | Verdict |
|---|---------|---------|
| 1 | `form_id` path-traversal validator wired into entrypoints | **Adopt.** `form_id` is a path component from MCP/CLI; defense-in-depth is missing. Use `re.fullmatch(^[A-Z]+(?:-[A-Z0-9]+)+$)`, length cap, reject non-str. The contract is already *tested* here by `evals/flow/test_form_id_contract.py`. |
| 2 | `is_canonical` defensive wrapper (non-dict input) | **Adopt.** MCP `fill_form` calls it on user JSON; non-dicts raise `TypeError`. `isinstance(case, dict) and _pkg_is_canonical(case)`. `evals/llm/test_input_robustness.py` asserts the boundary is total (skips with a pointer if not yet hardened). |
| 3 | `notary_state` override | **Adopt w/ care.** Mirrors the county pattern; default stays "Maine". If adopted, add `notary_state` to the canonical vocab. |
| 4 | B023 closure-over-loop-variable | **Adopt.** Cheap correctness hardening. |
| 5 | B905 `zip(..., strict=False)` | **Adopt.** Documents intent; no behavior change. |
| 6 | Dead-code cleanup + FDP-002A `facts.used` regen | **Adopt, verify regen.** The self-scan harvesting a dead variable is a real latent bug; already gated by `tests/test_required_facts.py`. |
| 7 | MCP `fill_form` surfaces preflight suggestion in error | **Adopt.** Pure UX win for agents that only read `error`. |
| 8 | New tests (form_id / canonical / recipe-integrity) | **Adopt.** The `known_orphans` lock is the repo's established anti-drift pattern; reused here as `KNOWN_PHANTOM_FORMS` and `DUAL_STATUS`. |
| 9 | `SECURITY.md` + contract docs | **Adopt.** |
| next | narrow ruff CI (F401/F541/F841/B023/B905) | **Adopt.** High-signal subset. |
| next | fuzz the MCP server | **Adopted as an eval** — `evals/llm/test_input_robustness.py`. |
| next | upstream `is_canonical` PR; wire/delete 10 orphan recipes | **Defer.** Upstream change set; orphans already locked by the audit's `test_recipe_integrity`. |

## Part B — The evaluation suite (`evals/`)

The audit's strongest finding was a **testing gap**: contracts with no
regression coverage. The existing `tests/` cover internal placement invariants
but nothing proves the end-to-end *agent contract* (`docs/agent-workflow.md`).
`evals/` fills that gap. Each eval names an **assumption → metric → pass bar**.
See `evals/README.md` for the catalog. Layers:

- **flow** — the 6 steps chain (routing recall, required-fact resolvability,
  form_id contract, preflight round-trip).
- **fill** — completed-form content is stable, correct, tier-honest
  (corpus-scale golden snapshots, trust-tier invariants, warning controls,
  PDF-gated `verify_fill`).
- **llm** — extraction fidelity (offline golden cases + live model scoring) and
  input robustness / fuzz.
- **vision** — semantic value-vs-label placement (opt-in).

Run: `python3 -m evals.run` (deterministic layers) / `--all` (gated layers).
Wired into CI alongside the existing `pytest tests/` gate.

### Findings surfaced by the evals on first run (2026-06-19)

The suite is also a measurement instrument. Its first run found, in the repo as
it stands:

1. **14 phantom routing targets.** `tools/smoke/fact_patterns.json` lists
   `expect_forms` ids with no `forms/<ID>/` directory: `CR-016, CR-028, CR-039,
   CR-040, CV-021, CV-035, CV-160, CV-168, CV-169, FM-030, FM-058, FM-059,
   PA-009, PC-160`. Recommendation: prune or repoint these (the smoke harness's
   routing assertions silently never matched them). Locked as
   `KNOWN_PHANTOM_FORMS` so no *new* phantom slips in.
2. **Deterministic routing recall ≈ 0.69** (top-5, over expected forms that
   exist). Useful but not high; criminal/PFA/guardianship narratives route
   weakest. The eval floors this at the current baseline to catch regressions;
   raise the bar as `tools/find_forms.py` keyword coverage improves.
3. **3 recipe-dispatched forms carry a non-`recipe` mapping status**
   (`CR-004, MJ-007, CR-198` → `opus-adjudicated`): legitimate dual-status
   (re-mapped after upstream drift while still recipe-dispatched), locked as
   `DUAL_STATUS`. The honest invariant is that a dispatched form is never
   labeled `no-mappable-fields`.
