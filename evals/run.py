"""Single entrypoint for the evaluation suite.

Runs the eval layers and prints an assumption -> result scorecard. Offline
layers (flow, fill) run by default; the llm/vision layers are gated by env
flags (MCF_EVAL_LLM / MCF_EVAL_VISION) and otherwise report SKIPPED.

    python3 -m evals.run                       # flow + fill (deterministic)
    python3 -m evals.run --layer flow          # one layer
    python3 -m evals.run --all                 # every discoverable layer
    python3 -m evals.run --json report.json    # machine-readable report

Each layer is a directory of unittest modules under evals/; this is just a
discovery + reporting wrapper over unittest, so `pytest evals/` works too.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
LAYERS = ["flow", "fill", "llm", "vision"]
DEFAULT = ["flow", "fill"]

# Assumption tested by each layer, for the scorecard header.
ASSUMPTIONS = {
    "flow": "the 6-step workflow chains (route->extract->preflight->fill)",
    "fill": "completed-form content is stable, correct, tier-honest",
    "llm": "an LLM extracts preflight-clean, required-fact-complete cases",
    "vision": "values land in the visually-correct widget",
}


def _run_layer(layer: str) -> dict:
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE / layer), pattern="test_*.py",
                            top_level_dir=str(REPO))
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stderr)
    result = runner.run(suite)
    return {
        "layer": layer,
        "assumption": ASSUMPTIONS.get(layer, ""),
        "tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "ok": result.wasSuccessful(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--layer", action="append", choices=LAYERS,
                    help="run only this layer (repeatable)")
    ap.add_argument("--all", action="store_true", help="run every layer")
    ap.add_argument("--json", type=pathlib.Path, help="write JSON report")
    args = ap.parse_args()

    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "tests"))

    layers = LAYERS if args.all else (args.layer or DEFAULT)
    reports = [_run_layer(layer) for layer in layers]

    print("\n" + "=" * 72)
    print("EVAL SCORECARD")
    print("=" * 72)
    for r in reports:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"[{status}] {r['layer']:7s} {r['tests']:3d} tests "
              f"({r['failures']} fail, {r['errors']} err, "
              f"{r['skipped']} skip)")
        print(f"         assumption: {r['assumption']}")
    print("=" * 72)

    if args.json:
        args.json.write_text(json.dumps(reports, indent=2) + "\n")
        print(f"report -> {args.json}")

    return 0 if all(r["ok"] for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
