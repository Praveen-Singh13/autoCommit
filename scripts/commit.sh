#!/bin/bash
# commit.sh — Stage all changes and commit with the provided message
# Usage: ./commit.sh "your commit message"

if [ -z "$1" ]; then
    echo "Error: No commit message provided."
    exit 1
fi

git add .
git commit -m "$1"
