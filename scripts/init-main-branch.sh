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

echo "Created main branch at current HEAD. Configure your remote default branch to main to avoid unrelated history errors."
