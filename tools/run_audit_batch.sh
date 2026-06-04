#!/usr/bin/env bash
# Phase 2 driver: fill -> cluster consensus audit -> Opus adjudication over a
# list of opus-reviewed forms (one ID per line in $1). Clean forms promote to
# `verified`; mismatch findings get an Opus mapping correction + re-audit;
# residual layout defects are recorded as render_flags. Commits every
# COMMIT_EVERY changes so a long run never loses progress. Safe to re-run:
# already-verified forms are skipped.
set -uo pipefail
cd "$(dirname "$0")/.."

LIST="${1:?usage: run_audit_batch.sh <form-list-file>}"
SAMPLES="${SAMPLES:-5}"
COMMIT_EVERY="${COMMIT_EVERY:-10}"
LOG="${LOG:-/tmp/audit_batch.log}"

export MCF_LLM_ENDPOINTS="http://localhost:8080/v1"
export MCF_VL_MODEL="qwen3.6-27b"
unset ANTHROPIC_API_KEY  # force subscription OAuth for the Opus adjudicator

: > "$LOG"
done=0; verified=0; flagged=0; failed=0; pending_commit=0
total=$(grep -c . "$LIST")
echo "audit batch start: $total forms, samples=$SAMPLES, commit every $COMMIT_EVERY" | tee -a "$LOG"

while read -r fid; do
  [ -n "$fid" ] || continue
  done=$((done+1))
  st=$(python3 -c "import json;print(json.load(open('forms/$fid/mapping.json')).get('status','?'))" 2>/dev/null)
  if [ "$st" = "verified" ]; then
    echo "[$done/$total] $fid: skip (already verified)" | tee -a "$LOG"; continue
  fi
  out=$(python3 tools/audit_loop.py --forms "$fid" --qwen-samples "$SAMPLES" --max-iters 2 2>>"$LOG")
  echo "[$done/$total] $out" | tee -a "$LOG"
  if echo "$out" | grep -q ": verified"; then
    verified=$((verified+1)); pending_commit=$((pending_commit+1))
  elif echo "$out" | grep -qE "render-flagged|party-conflict|opus-residual"; then
    flagged=$((flagged+1)); pending_commit=$((pending_commit+1))
  elif echo "$out" | grep -qE "audit-failed|fill-error"; then
    failed=$((failed+1))
  fi
  if [ "$pending_commit" -ge "$COMMIT_EVERY" ]; then
    git add forms/*/mapping.json
    git commit -q -m "Phase 2: audit-verify $pending_commit mappings" \
      -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>" \
      && git push -q origin HEAD:main && echo "  -- committed+pushed $pending_commit --" | tee -a "$LOG"
    pending_commit=0
  fi
done < "$LIST"

if ! git diff --quiet forms/*/mapping.json; then
  git add forms/*/mapping.json
  git commit -q -m "Phase 2: audit-verify final $pending_commit mappings" \
    -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>" \
    && git push -q origin HEAD:main && echo "  -- final commit+push --" | tee -a "$LOG"
fi
echo "audit batch done: $done processed, $verified verified, $flagged render-flagged, $failed failed" | tee -a "$LOG"
