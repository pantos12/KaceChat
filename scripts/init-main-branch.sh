#!/usr/bin/env bash
set -euo pipefail

if git show-ref --quiet refs/heads/main; then
  echo "main branch already exists"
  exit 0
fi

current_branch=$(git branch --show-current)

git branch main

git symbolic-ref HEAD refs/heads/main

if [ "$current_branch" != "main" ]; then
  git checkout "$current_branch"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main || true
fi

echo "Created main branch at current HEAD. Configure your remote default branch to main to avoid unrelated history errors."
