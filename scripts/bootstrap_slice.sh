#!/usr/bin/env bash
# Bootstrap a new slice for the fables.gg gap-closing roadmap.
#
# Usage: scripts/bootstrap_slice.sh A1
#
# - Validates slice ID against the manifest below.
# - Creates branch `track-{x}/{ID}-{kebab-title}` off main.
# - Creates worktree at `~/ares-track-{x}/{ID}`.
# - Copies workstream template to docs/development/workstreams/.
# - Empty-commits the doc and pushes the branch.
# - Optionally opens a draft PR if `gh` is available.
#
# Idempotent: re-running for an already-bootstrapped slice prints status and exits 0.

set -euo pipefail

SLICE_ID="${1:-}"
if [[ -z "$SLICE_ID" ]]; then
  echo "usage: $0 <slice-id>  (e.g. A1, B3, C2)"
  exit 2
fi

# Slice manifest. Track these alongside ~/.claude/plans/a-i-happy-matsumoto.md.
declare -A SLICE_TITLES=(
  [A1]="dice-skill-checks"
  [A2]="itemized-inventory"
  [A3]="conditions"
  [A4]="combat-mode"
  [A5]="ability-registry"
  [B1]="media-provider"
  [B2]="scene-art"
  [B3]="portraits"
  [B4]="tts-narration"
  [B5]="world-map"
  [C1]="admin-api"
  [C2]="operator-app"
  [C3]="lore-pages"
  [C4]="session-prep"
  [C5]="continuity-review"
)

if [[ -z "${SLICE_TITLES[$SLICE_ID]+x}" ]]; then
  echo "error: unknown slice id '$SLICE_ID'"
  echo "known: ${!SLICE_TITLES[*]}"
  exit 2
fi

TITLE="${SLICE_TITLES[$SLICE_ID]}"
TRACK_LETTER="$(echo "$SLICE_ID" | cut -c1 | tr 'A-Z' 'a-z')"
BRANCH="track-${TRACK_LETTER}/${SLICE_ID}-${TITLE}"
WORKTREE_DIR="${ARES_WORKTREE_ROOT:-$HOME}/ares-track-${TRACK_LETTER}/${SLICE_ID}"
DOC_PATH="docs/development/workstreams/${SLICE_ID}-${TITLE}.md"
TEMPLATE_PATH="docs/development/workstreams/_template.md"

# Resolve repo root (this script lives in scripts/).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "error: template not found at $TEMPLATE_PATH"
  exit 1
fi

# If branch already exists, just report and exit.
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "branch already exists: $BRANCH"
  if [[ -d "$WORKTREE_DIR" ]]; then
    echo "worktree already exists: $WORKTREE_DIR"
  else
    echo "creating worktree at: $WORKTREE_DIR"
    git worktree add "$WORKTREE_DIR" "$BRANCH"
  fi
  echo "doc: $REPO_ROOT/$DOC_PATH"
  exit 0
fi

# Create branch off main without disturbing current checkout.
echo "creating branch: $BRANCH (off main)"
git branch "$BRANCH" main

# Create worktree.
echo "creating worktree: $WORKTREE_DIR"
mkdir -p "$(dirname "$WORKTREE_DIR")"
git worktree add "$WORKTREE_DIR" "$BRANCH"

# Copy template into the worktree.
WT_DOC="$WORKTREE_DIR/$DOC_PATH"
mkdir -p "$(dirname "$WT_DOC")"
sed \
  -e "s|{ID}|$SLICE_ID|g" \
  -e "s|{Title}|$(echo "$TITLE" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')|g" \
  -e "s|{kebab-title}|$TITLE|g" \
  -e "s|{x}|$TRACK_LETTER|g" \
  "$TEMPLATE_PATH" > "$WT_DOC"

# Initial commit so the next agent has something to anchor on.
(
  cd "$WORKTREE_DIR"
  git add "$DOC_PATH"
  git commit -m "chore($SLICE_ID): bootstrap slice — branch + workstream doc

Slice $SLICE_ID ($TITLE) opened from main per the parent roadmap at
~/.claude/plans/a-i-happy-matsumoto.md.

Status: not-started. See docs/development/agent-handoff-protocol.md for
the resume procedure."
)

echo
echo "bootstrap complete:"
echo "  branch:    $BRANCH"
echo "  worktree:  $WORKTREE_DIR"
echo "  doc:       $REPO_ROOT/$DOC_PATH"
echo
echo "next steps:"
echo "  1. cd $WORKTREE_DIR"
echo "  2. edit $DOC_PATH (Goal, Next concrete step)"
echo "  3. git push -u origin $BRANCH"
echo "  4. gh pr create --draft --title \"$SLICE_ID: $TITLE\" --body-file $DOC_PATH"
