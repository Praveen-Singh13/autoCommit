#!/bin/bash
# get_diff.sh — Fetch combined git diff (unstaged + staged)

echo "=== Unstaged Changes ==="
git diff

echo ""
echo "=== Staged Changes ==="
git diff --cached
