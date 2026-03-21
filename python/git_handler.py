"""
AutoCommit — git_handler.py
Handles all Git CLI interactions via Python subprocess.
"""

import subprocess


def _run_git(args, cwd=None):
    """
    Run a git command and return (success, stdout).
    Returns (False, stderr) on failure.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "git is not installed or not in PATH"
    except subprocess.TimeoutExpired:
        return False, "git command timed out"


def is_git_repo(cwd=None):
    """Check if the current/given directory is inside a Git work tree."""
    success, _ = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    return success


def get_git_diff(cwd=None):
    """
    Return the combined diff (unstaged + staged).
    Returns an empty string if there are no changes.
    """
    _, unstaged = _run_git(["diff"], cwd=cwd)
    _, staged = _run_git(["diff", "--cached"], cwd=cwd)

    parts = []
    if unstaged:
        parts.append(unstaged)
    if staged:
        parts.append(staged)
    return "\n".join(parts)


def get_branch_name(cwd=None):
    """Return the current branch name, or 'HEAD' if detached."""
    success, branch = _run_git(["branch", "--show-current"], cwd=cwd)
    if success and branch:
        return branch
    return "HEAD"


def get_changed_files(cwd=None):
    """Return a list of changed file paths (porcelain format)."""
    success, output = _run_git(["status", "--porcelain"], cwd=cwd)
    if not success or not output:
        return []
    files = []
    for line in output.splitlines():
        # porcelain format: XY filename  (first 3 chars are status + space)
        if len(line) > 3:
            files.append(line[3:].strip())
    return files


def run_commit(commit_message, cwd=None):
    """
    Stage all changes with 'git add .' and commit with the given message.
    Returns (success: bool, output: str).
    """
    # Stage everything
    add_ok, add_out = _run_git(["add", "."], cwd=cwd)
    if not add_ok:
        return False, f"git add failed: {add_out}"

    # Commit
    commit_ok, commit_out = _run_git(["commit", "-m", commit_message], cwd=cwd)
    if not commit_ok:
        return False, f"git commit failed: {commit_out}"

    return True, commit_out


# ──────────────────────────────────────────────
# Quick self-test when run directly
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import os

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Testing against repo: {repo}\n")

    print(f"1. is_git_repo()  => {is_git_repo(cwd=repo)}")
    print(f"2. get_branch_name() => {get_branch_name(cwd=repo)}")

    changed = get_changed_files(cwd=repo)
    print(f"3. get_changed_files() => {changed}")

    diff = get_git_diff(cwd=repo)
    preview = diff[:300] if diff else "(no diff)"
    print(f"4. get_git_diff() (first 300 chars):\n{preview}")

    print("\n✅ git_handler.py self-test complete.")
    print("   (run_commit was NOT tested to avoid accidental commits)")
