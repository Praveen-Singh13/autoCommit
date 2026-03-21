"""
AutoCommit — main.py
Entry point: orchestrates git detection, diff fetching, AI message generation, and commit.
Outputs JSON to stdout for the VS Code extension to parse.
"""

import json
import os
import sys

# Ensure the python/ directory is on the path so imports work
# regardless of how the script is invoked.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_handler import is_git_repo, get_git_diff, get_branch_name, get_changed_files, run_commit
from api_handler import generate_commit_message


def _output(status, message, commit_message=None):
    """Print a JSON result to stdout and return the exit code."""
    result = {"status": status, "message": message}
    if commit_message:
        result["commit_message"] = commit_message
    print(json.dumps(result))
    return 0 if status == "success" else 1


def main():
    """
    Full AutoCommit pipeline:
    1. Verify we're inside a Git repo
    2. Check for uncommitted changes
    3. Fetch diff + branch name
    4. Generate commit message via AI
    5. Stage & commit
    """

    # Accept optional working directory argument
    cwd = sys.argv[1] if len(sys.argv) > 1 else None

    # Step 1 — Verify Git repo
    if not is_git_repo(cwd=cwd):
        sys.exit(_output("error", "Not a git repository"))

    # Step 2 — Check for changes
    changed_files = get_changed_files(cwd=cwd)
    if not changed_files:
        sys.exit(_output("success", "No changes detected"))

    # Step 3 — Fetch diff and branch
    diff = get_git_diff(cwd=cwd)
    branch = get_branch_name(cwd=cwd)

    if not diff:
        # There are changed files but no diff (e.g. only untracked new files)
        # Build a minimal description from the file list
        diff = "New/untracked files:\n" + "\n".join(f"  + {f}" for f in changed_files)

    print(f"[AutoCommit] {len(changed_files)} file(s) changed on branch '{branch}'", file=sys.stderr)

    # Step 4 — Generate commit message
    commit_msg = generate_commit_message(diff, branch)
    print(f"[AutoCommit] Generated message: {commit_msg!r}", file=sys.stderr)

    # Step 5 — Stage and commit
    success, output = run_commit(commit_msg, cwd=cwd)
    if not success:
        sys.exit(_output("error", output, commit_message=commit_msg))

    sys.exit(_output("success", output, commit_message=commit_msg))


if __name__ == "__main__":
    main()
