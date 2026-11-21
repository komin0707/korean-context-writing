#!/usr/bin/env bash
# Sync explicit feedback to an already-configured private Git remote.
# Requires Git, permissions, and internet. Does not configure remote or create a repository.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git rev-parse --show-toplevel >/dev/null 2>&1 || ! git remote get-url origin >/dev/null 2>&1; then
  echo "Git origin is not configured. See SETUP_PERSISTENCE.md" >&2
  exit 2
fi
git add memory/feedback.jsonl
if ! git diff --cached --quiet; then
  git commit -m "Persist explicit Korean-writing feedback"
fi
git pull --rebase origin "$(git branch --show-current)"
git push origin "$(git branch --show-current)"
echo "Synced feedback to origin."
