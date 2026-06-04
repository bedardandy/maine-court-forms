#!/usr/bin/env bash
# Paced driver for improve_loop over a list of form IDs (one per line in $1).
# Promotes vision-mapped drafts via the Opus judge; your local VLM endpoint(s)
# feed the Qwen draft/remap step. Commits every COMMIT_EVERY promotions so a
# long run never loses progress. Safe to re-run: already-opus-reviewed forms
# are skipped. Pass --remap as $2 to have Qwen re-draft first (coverage track).
set -uo pipefail
cd "$(dirname "$0")/.."

LIST="${1:?usage: run_improve_batch.sh <form-list-file> [--remap]}"
REMAP="${2:-}"
COMMIT_EVERY="${COMMIT_EVERY:-15}"
LOG="${LOG:-/tmp/improve_batch.log}"

export MCF_LLM_ENDPOINTS="http://localhost:8080/v1"
export MCF_VL_MODEL="qwen3.6-27b"
unset ANTHROPIC_API_KEY  # force subscription OAuth for the Opus judge

: > "$LOG"
done=0; promoted=0; failed=0; pending_commit=0
total=$(grep -c . "$LIST")
# In --author mode, re-process already-opus-reviewed forms (Opus can still
# author keys for fields a prior correct-only pass left unmapped). In plain
# review mode, skip them (idempotent re-runs).
case "$REMAP" in *author*) skip_reviewed=0 ;; *) skip_reviewed=1 ;; esac
echo "batch start: $total forms, flags='$REMAP', skip_reviewed=$skip_reviewed, commit every $COMMIT_EVERY" | tee -a "$LOG"

while read -r fid; do
  [ -n "$fid" ] || continue
  done=$((done+1))
  st=$(python3 -c "import json;print(json.load(open('forms/$fid/mapping.json')).get('status','?'))" 2>/dev/null)
  if [ "$st" = "opus-reviewed" ] && [ "$skip_reviewed" = "1" ]; then
    echo "[$done/$total] $fid: skip (already opus-reviewed)" | tee -a "$LOG"; continue
  fi
  out=$(python3 tools/improve_loop.py --forms "$fid" $REMAP --max-iters 2 2>>"$LOG")
  echo "[$done/$total] $out" | tee -a "$LOG"
  if echo "$out" | grep -q "opus-reviewed"; then
    promoted=$((promoted+1)); pending_commit=$((pending_commit+1))
  elif echo "$out" | grep -q "review-failed"; then
    failed=$((failed+1))
  fi
  if [ "$pending_commit" -ge "$COMMIT_EVERY" ]; then
    git add forms/*/mapping.json
    git commit -q -m "Loop: promote $pending_commit mappings to opus-reviewed" \
      -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>" \
      && git push -q origin HEAD:main && echo "  -- committed+pushed $pending_commit --" | tee -a "$LOG"
    pending_commit=0
  fi
done < "$LIST"

# final flush
if ! git diff --quiet forms/*/mapping.json; then
  git add forms/*/mapping.json
  git commit -q -m "Loop: promote final $pending_commit mappings to opus-reviewed" \
    -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>" \
    && git push -q origin HEAD:main && echo "  -- final commit+push --" | tee -a "$LOG"
fi
echo "batch done: $done processed, $promoted promoted, $failed review-failed" | tee -a "$LOG"
