"""EVAL — Assumption: the yellow-light warning layers are sound — they fire on
real contradictions and stay silent on clean input.

CLAUDE.md promises constraint/computation warnings are "warnings, never blocks"
that "list problems for a human to resolve". For an automation consumer that
trust is only useful if the signal is real: a warning that never fires is
useless, and one that false-positives on clean data trains agents to ignore it.

This eval builds positive controls (crafted contradictions that MUST fire) and
negative controls (clean values that MUST stay silent) for every shipped
constraints.json / computations.json, exercising the same engine evaluators the
fill path uses (maine_forms_engine.constraints / .computations).

Metric:   controls that misbehave (fired-clean or silent-on-contradiction).
Pass bar: zero.
"""
from __future__ import annotations

import unittest

from evals.common import FORMS
from maine_forms_engine.constraints import evaluate as k_eval
from maine_forms_engine.constraints import load_constraints
from maine_forms_engine.computations import evaluate as c_eval
from maine_forms_engine.computations import load_computations


def _constraint_forms():
    return sorted(p.parent.name for p in FORMS.glob("*/constraints.json"))


def _computation_forms():
    return sorted(p.parent.name for p in FORMS.glob("*/computations.json"))


class TestConstraintControls(unittest.TestCase):
    def test_mutually_exclusive_groups_fire_and_stay_silent(self):
        for fid in _constraint_forms():
            cfg = load_constraints(FORMS / fid)
            groups = (cfg or {}).get("mutually_exclusive") or []
            for grp in groups:
                keys = grp["keys"] if isinstance(grp, dict) else grp
                if len(keys) < 2:
                    continue
                with self.subTest(form=fid, keys=keys):
                    # positive control: two boxes checked -> must fire
                    hot = {keys[0]: "X", keys[1]: "X"}
                    fired = [w for w in k_eval(cfg, hot)
                             if w["code"] == "MUTUALLY_EXCLUSIVE"]
                    self.assertTrue(
                        fired, f"{fid}: paradox {keys[:2]} did not fire")
                    # negative control: one box checked -> must stay silent
                    one = {keys[0]: "X"}
                    quiet = [w for w in k_eval(cfg, one)
                             if w["code"] == "MUTUALLY_EXCLUSIVE"]
                    self.assertFalse(
                        quiet, f"{fid}: single selection false-fired")


class TestComputationControls(unittest.TestCase):
    def test_sum_computations_compute_and_detect_mismatch(self):
        for fid in _computation_forms():
            cfg = load_computations(FORMS / fid)
            for target, spec in (cfg or {}).get("computed", {}).items():
                if spec.get("op") not in ("sum", "product"):
                    continue
                inputs = spec.get("inputs") or []
                if len(inputs) < 2:
                    continue
                with self.subTest(form=fid, target=target):
                    base = {k: "2" for k in inputs}
                    # negative control: omit target -> computed, no warning
                    clean = c_eval(cfg, dict(base))
                    self.assertFalse(
                        [w for w in clean["warnings"]
                         if w.get("key") == target],
                        f"{fid}/{target}: clean input warned")
                    computed_keys = {c["key"] for c in clean["computed"]}
                    self.assertIn(
                        target, computed_keys,
                        f"{fid}/{target}: omitted target was not computed")
                    # positive control: supply a wrong target -> MISMATCH
                    bad = dict(base)
                    bad[target] = "999999"
                    warned = [w for w in c_eval(cfg, bad)["warnings"]
                              if w.get("key") == target
                              and w["code"] == "COMPUTATION_MISMATCH"]
                    self.assertTrue(
                        warned,
                        f"{fid}/{target}: contradiction not flagged")


if __name__ == "__main__":
    unittest.main()
