#!/usr/bin/env python3
"""A small, safe if/then expression engine for per-form fill logic.

This is the evaluator behind ``forms/<ID>/logic.json`` — authored + derived
cross-field rules (conditional-required, attachment/companion-form triggers,
value incompatibilities, and value inferences). Like the constraints and
computations layers, it is **warnings-only**: a firing rule never blocks or
alters a fill; it tells a human/automation what else the form needs.

Expression language (JSON, deterministic, total — never raises):

    {"var": "facts.x"}            value at a case path or "field:<id>"
    {"and": [e, ...]} / {"or": [...]} / {"not": e}
    {"==": [a, b]} / {"!=": [...]} / {"<": [...]} / {"<=": / ">": / ">=":}
    {"in": [a, [..]]}             membership
    {"contains": [a, b]}          substring / list membership
    {"matches": [a, "regex"]}     regex search (case-insensitive)
    {"present": "path"} / {"absent": "path"} / {"truthy": "path"}

Operands are either an expression, a ``{"var": path}``, a bare path string in
the present/absent/truthy forms, or a JSON literal. A path is resolved against
the evaluation context: ``facts.*`` / ``matter.*`` / ``parties.*`` / ``party.*``
read the canonical case; ``field:<field_id>`` reads a resolved widget value.

Rule kinds (the ``then`` action determines the warning emitted):

    conditional_required  then.require: [paths] — fires if `when` and any
                          required path is absent.
    attachment            then.attachment: "<doc>" — fires when `when` true.
    companion_form        then.form: "<ID>" (+ required) — fires when `when`.
    incompatible          fires when `when` (the contradiction) is true.
    value_inference       then.suggest: "<text>" — a non-binding suggestion.
    note                  fires when `when`; generic message.
"""
from __future__ import annotations

import re

_MISSING = object()


def _resolve(path: str, ctx: dict):
    """Resolve a dotted case path or 'field:<id>' against the context."""
    if not isinstance(path, str):
        return path
    if path.startswith("field:"):
        return (ctx.get("fields") or {}).get(path[6:], _MISSING)
    cur = ctx.get("case") or {}
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return _MISSING
    return cur


def _is_present(v) -> bool:
    return v is not _MISSING and v not in (None, "", [], {})


def _operand(node, ctx):
    """A var-node, a bare path string, or a literal."""
    if isinstance(node, dict) and set(node) == {"var"}:
        v = _resolve(node["var"], ctx)
        return None if v is _MISSING else v
    if isinstance(node, dict):  # nested expression
        return evaluate(node, ctx)
    return node  # literal


def _num(v):
    try:
        return float(str(v).lstrip("$").replace(",", "").rstrip("%"))
    except (TypeError, ValueError):
        return None


def evaluate(expr, ctx) -> bool:
    """Evaluate a boolean expression. Unknown/missing data is falsy; never
    raises."""
    if not isinstance(expr, dict) or not expr:
        return bool(expr)
    op, arg = next(iter(expr.items()))
    try:
        if op == "and":
            return all(evaluate(e, ctx) for e in arg)
        if op == "or":
            return any(evaluate(e, ctx) for e in arg)
        if op == "not":
            return not evaluate(arg, ctx)
        if op in ("present", "truthy"):
            v = _resolve(arg, ctx)
            return _is_present(v) and (str(v).strip().lower() not in
                                       ("", "false", "no", "off", "0", "n")
                                       if op == "truthy" else True)
        if op == "absent":
            return not _is_present(_resolve(arg, ctx))
        if op == "var":  # truthiness of a var used as a condition
            return _is_present(_operand(expr, ctx))
        a, b = (_operand(arg[0], ctx), _operand(arg[1], ctx)) \
            if op != "in" else (_operand(arg[0], ctx), arg[1])
        if op == "==":
            return _eq(a, b)
        if op == "!=":
            return not _eq(a, b)
        if op == "in":
            return any(_eq(a, x) for x in (b or []))
        if op == "contains":
            if isinstance(a, (list, tuple)):
                return any(_eq(x, b) for x in a)
            return b is not None and str(b).lower() in str(a or "").lower()
        if op == "matches":
            return bool(re.search(str(b), str(a or ""), re.I)) if a is not None \
                else False
        if op in ("<", "<=", ">", ">="):
            na, nb = _num(a), _num(b)
            if na is None or nb is None:
                return False
            return {"<": na < nb, "<=": na <= nb,
                    ">": na > nb, ">=": na >= nb}[op]
    except Exception:  # noqa: BLE001 — evaluator is total
        return False
    return False


def _eq(a, b) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b)
    na, nb = _num(a), _num(b)
    if na is not None and nb is not None:
        return na == nb
    return str(a).strip().lower() == str(b).strip().lower()


def evaluate_rules(logic: dict, case: dict,
                   fields: dict | None = None) -> list[dict]:
    """Evaluate a form's logic.json against a canonical case (+ optional
    resolved field values). Returns a list of warning dicts; never raises."""
    if not isinstance(logic, dict):
        return []
    ctx = {"case": case if isinstance(case, dict) else {},
           "fields": fields or {}}
    out: list[dict] = []
    for rule in logic.get("rules") or []:
        try:
            warn = _eval_rule(rule, ctx)
        except Exception:  # noqa: BLE001
            warn = None
        if warn:
            out.append(warn)
    return out


def _eval_rule(rule: dict, ctx: dict) -> dict | None:
    kind = rule.get("kind")
    when = rule.get("when")
    fired = evaluate(when, ctx) if when is not None else True
    then = rule.get("then") or {}

    if kind == "conditional_required":
        if not fired:
            return None
        missing = [p for p in (then.get("require") or [])
                   if not _is_present(_resolve(p, ctx))]
        if not missing:
            return None
        detail = {"missing": missing}
        default_msg = (f"these are required when this condition holds but are "
                       f"missing: {missing}")
    elif kind == "incompatible":
        if not fired:
            return None
        detail = {}
        default_msg = "these selections are logically incompatible"
    elif kind == "attachment":
        if not fired:
            return None
        detail = {"attachment": then.get("attachment")}
        default_msg = (f"this selection expects an attachment: "
                       f"{then.get('attachment')}")
    elif kind == "companion_form":
        if not fired:
            return None
        detail = {"form": then.get("form"),
                  "required": bool(then.get("required"))}
        default_msg = (f"{'requires' if then.get('required') else 'is usually '
                       'filed with'} companion form {then.get('form')}")
    elif kind == "value_inference":
        if not fired:
            return None
        detail = {"suggest": then.get("suggest")}
        default_msg = then.get("suggest") or "review this value"
    elif kind == "note":
        if not fired:
            return None
        detail = {}
        default_msg = "review this rule"
    else:
        return None

    warn = {
        "code": "logic",
        "rule_id": rule.get("id"),
        "kind": kind,
        "severity": rule.get("severity", "warning"),
        "message": rule.get("message") or default_msg,
        **detail,
    }
    if rule.get("authority"):
        warn["authority"] = rule["authority"]
    return warn
