"""
AutoCommit — api_handler.py
Handles AI API calls for commit message generation.
Supports Google Gemini and OpenAI-compatible endpoints.
"""

import json
import os

try:
    import requests
except ImportError:
    requests = None


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

MAX_DIFF_CHARS = 8000

FALLBACK_MESSAGE = "update project files"

SYSTEM_PROMPT = """You are an expert developer writing Git commit messages.
Given a git diff and branch name, generate a concise, professional commit message
following the Conventional Commits format.

Rules:
1. First line: type(scope): short description (max 72 chars)
   Types: feat, fix, refactor, docs, style, test, chore, perf, ci, build
2. Leave a blank line after the first line
3. Optionally add bullet points describing key changes (prefix with -)
4. Do NOT include any explanation, markdown formatting, or code fences
5. Output ONLY the commit message text, nothing else

Example output:
feat(auth): add login validation logic

- Added password strength validation
- Improved error handling for failed attempts
"""


def _get_config_path():
    """Resolve the path to config/config.json relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", "config", "config.json")


def load_config():
    """
    Load API configuration from config/config.json.
    Falls back to environment variables if the file is missing or incomplete.
    Returns dict with keys: api_key, api_url, api_provider, model.
    """
    config = {
        "api_provider": "gemini",
        "api_key": "",
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "model": "gemini-2.0-flash",
    }

    # Try loading from file
    config_path = _get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
            config.update({k: v for k, v in file_config.items() if v})
        except (json.JSONDecodeError, IOError):
            pass

    # Environment variables override file config
    env_key = os.environ.get("AUTOCOMMIT_API_KEY")
    env_url = os.environ.get("AUTOCOMMIT_API_URL")
    env_model = os.environ.get("AUTOCOMMIT_MODEL")
    env_provider = os.environ.get("AUTOCOMMIT_API_PROVIDER")
    if env_key:
        config["api_key"] = env_key
    if env_url:
        config["api_url"] = env_url
    if env_model:
        config["model"] = env_model
    if env_provider:
        config["api_provider"] = env_provider

    return config


def _truncate_diff(diff, max_chars=MAX_DIFF_CHARS):
    """Truncate diff to stay within token limits."""
    if len(diff) <= max_chars:
        return diff
    return diff[:max_chars] + f"\n\n... [truncated, {len(diff) - max_chars} chars omitted]"


# ──────────────────────────────────────────────
# Gemini API
# ──────────────────────────────────────────────

def _call_gemini(config, user_prompt):
    """
    Call Google Gemini API (generateContent endpoint).
    API key is passed as a query parameter.
    """
    model = config["model"]
    base_url = config["api_url"].rstrip("/")
    url = f"{base_url}/{model}:generateContent"

    response = requests.post(
        url,
        params={"key": config["api_key"]},
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 256,
            },
        },
        timeout=15,
    )

    if response.status_code != 200:
        print(f"Warning: Gemini API returned status {response.status_code}. Using fallback.")
        return None

    data = response.json()
    # Gemini response: data.candidates[0].content.parts[0].text
    message = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return message if message else None


# ──────────────────────────────────────────────
# OpenAI-compatible API
# ──────────────────────────────────────────────

def _call_openai(config, user_prompt):
    """Call OpenAI-compatible chat completions endpoint."""
    response = requests.post(
        config["api_url"],
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": config["model"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 256,
        },
        timeout=15,
    )

    if response.status_code != 200:
        print(f"Warning: OpenAI API returned status {response.status_code}. Using fallback.")
        return None

    data = response.json()
    message = data["choices"][0]["message"]["content"].strip()
    return message if message else None


# ──────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────

def generate_commit_message(diff, branch):
    """
    Send diff and branch info to the configured AI API and return a commit message string.
    On any failure, returns the fallback message.
    """
    if not requests:
        print("Warning: 'requests' module not installed. Using fallback message.")
        return FALLBACK_MESSAGE

    config = load_config()
    api_key = config["api_key"]
    provider = config["api_provider"]

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Warning: No valid API key configured. Using fallback message.")
        return FALLBACK_MESSAGE

    # Truncate large diffs
    truncated_diff = _truncate_diff(diff)

    # Build the user prompt
    user_prompt = f"Branch: {branch}\n\nGit Diff:\n```\n{truncated_diff}\n```"

    try:
        if provider == "gemini":
            message = _call_gemini(config, user_prompt)
        else:
            message = _call_openai(config, user_prompt)

        return message if message else FALLBACK_MESSAGE

    except requests.exceptions.Timeout:
        print("Warning: API request timed out. Using fallback message.")
        return FALLBACK_MESSAGE
    except requests.exceptions.ConnectionError:
        print("Warning: Could not connect to API. Using fallback message.")
        return FALLBACK_MESSAGE
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to parse API response ({e}). Using fallback message.")
        return FALLBACK_MESSAGE
    except Exception as e:
        print(f"Warning: Unexpected error ({e}). Using fallback message.")
        return FALLBACK_MESSAGE


# ──────────────────────────────────────────────
# Self-test when run directly
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== api_handler.py self-test ===\n")

    cfg = load_config()
    print(f"Config loaded:")
    print(f"  provider: {cfg['api_provider']}")
    print(f"  api_url:  {cfg['api_url']}")
    print(f"  model:    {cfg['model']}")
    print(f"  api_key:  {'****' + cfg['api_key'][-4:] if len(cfg['api_key']) > 4 else '(not set)'}")
    print()

    test_diff = """diff --git a/utils.py b/utils.py
--- a/utils.py
+++ b/utils.py
@@ -10,6 +10,12 @@ def process_data(data):
     result = []
     for item in data:
         result.append(item.strip())
+    if not data:
+        raise ValueError("Input data cannot be empty")
+    logger.info(f"Processing {len(data)} items")
     return result
"""

    print(f"Sending test diff ({len(test_diff)} chars) on branch 'feature/validation'...")
    message = generate_commit_message(test_diff, "feature/validation")
    print(f"\nGenerated commit message:\n---\n{message}\n---")
    print("\n✅ api_handler.py self-test complete.")
