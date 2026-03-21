# 🤖 AutoCommit — Claude Code Implementation Workflow

**Objective:** Build the AutoCommit VS Code extension exactly as described in the PRD, step-by-step.
**Strategy:** To avoid getting stuck in infinite loops or hallucinating due to context limits, this workflow breaks the project into small, isolated, and testable blocks of logic. **Complete each block fully before moving to the next.**

---

## 🏗️ Phase 1: Project Scaffolding
**Goal:** Setup the VS Code extension boilerplate and empty Python scripts.

**Steps:**
1. **Initialize VS Code Extension:**
   - Use `yo code` or manually create the extension boilerplate in a folder (e.g., `autoCommit/`).
   - Define the `package.json` with a single command contribution: `autocommit.triggerCommit`.
2. **Create Directory Structure:**
   - Create directories: `python/`, `scripts/`, `config/`.
   - Create empty Python files: `python/main.py`, `python/git_handler.py`, `python/api_handler.py`.
3. **Verify Block:** Check that the extension boilerplate compiles and can be launched in a debug host without errors.

---

## ⚙️ Phase 2: Python Git Integration (`git_handler.py`)
**Goal:** Extract diffs and Git status using Python's `subprocess` module.

**Steps:**
1. **Check Git Repository Status:**
   - Write a function `is_git_repo()` that runs `git status --porcelain`.
   - Return false or handle gracefully if "Not a git repository".
2. **Fetch Diffs:**
   - Write a function `get_git_diff()` that runs `git diff` and `git diff --cached`.
   - Combine both outputs. Handle the case where there is no diff (i.e., NO changes).
3. **Fetch Branch Name:**
   - Write a function `get_branch_name()` running `git branch --show-current`.
4. **Commit Execution:**
   - Write a function `run_commit(commit_message)` that executes `git add .` followed by `git commit -m "<commit_message>"`.
5. **Verify Block:** Run `git_handler.py` directly from the terminal to ensure it correctly prints the current repository's diff and branch name. Do not proceed until git CLI commands are working correctly from Python.

---

## 🧠 Phase 3: AI API Integration (`api_handler.py`)
**Goal:** Connect to the AI Provider to generate a commit message.

**Steps:**
1. **Load Configuration:**
   - Write a module to load API keys securely (e.g., from `config/config.json` or environment variables passed by VS Code).
2. **API Interaction:**
   - Write a function `generate_commit_message(diff, branch)`.
   - Send the diff and branch context via `requests.post()` to the AI endpoint. Use a standardized prompt asking for a concise commit message.
3. **Error Handling:**
   - Implement `try/except` blocks. If the API fails (timeout, 401 invalid key, etc.), immediately fallback to returning `"update project files"`.
4. **Verify Block:** Manually pass a hardcoded diff string to `generate_commit_message()` and print the response to ensure the API call succeeds and returns just a message.

---

## 🧩 Phase 4: Python Orchestrator (`main.py`)
**Goal:** Connect Phase 2 and Phase 3 together into a single, executed pipeline.

**Steps:**
1. **Pipeline Logic:**
   - Call `is_git_repo()`. If false, `sys.exit(1)` with a message.
   - Call `get_git_diff()`. If empty, `sys.exit(0)` with "No changes detected".
   - Pass the returned diff context to `generate_commit_message()`.
   - Call `run_commit(message)` with the returned AI message.
2. **Verify Block:** Make a real modification to a dummy file, run `python main.py` directly from the terminal, and verify that the file gets automatically committed with an AI-generated message.

---

## 🔌 Phase 5: VS Code Extension Integration (`extension.js`)
**Goal:** Bind the Python script to VS Code commands and lifecycle events.

**Steps:**
1. **Manual Command Palette Execution:**
   - Inside `extension.js`, in the `autocommit.triggerCommit` function, use Node's `child_process.exec` or `spawn` to run `python main.py`.
   - Provide VS Code UI feedback: use `vscode.window.withProgress` or `showInformationMessage` while generating, and show success/error notifications when done.
2. **On VS Code Close Listener:**
   - Explore and implement triggers that fire when the window is closed, executing the command in the background (if feasible within VS Code's extension sandbox).
3. **Verify Block:** Install the extension locally, make a change, hit `Ctrl+Shift+P` -> AutoCommit, and check the git history.

---

## 🛡️ Phase 6: Edge Cases & Polish
**Goal:** Finalize performance, security, and edge cases.

**Steps:**
1. **Context Limits:** Ensure large diffs don't crash the API. Truncate diffs string length if it exceeds typical LLM token limits.
2. **Secret Management:** Ensure API keys are handled securely (preferably using VS Code SecretStorage rather than a plaintext json config, then pass via process environment variable to python).
3. **Verify Block:** Test with an intentionally broken API key. Test with an empty git repository. Over-test failure modes.

---

**Claude Instructions:** Start with Phase 1. Complete each phase sequentially. **Do not attempt to write the entire codebase in one single output.** Verify at the end of each phase explicitly before proceeding to the next.
