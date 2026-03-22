# 🤖 Auto-Commit! — Intelligent Commit Message Generator

> **Automatically generate clean, professional, human-like Git commit messages — powered by AI.**

[![VS Code Marketplace](https://img.shields.io/visual-studio-marketplace/v/PraveenSingh13.auto-commit13?label=VS%20Code%20Marketplace&color=blue)](https://marketplace.visualstudio.com/items?itemName=PraveenSingh13.auto-commit13)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 📌 What is Auto-Commit?

**Auto-Commit!** is a VS Code extension that eliminates the hassle of writing commit messages. It detects your uncommitted changes, sends them to an AI model (Google Gemini or OpenAI), and generates a meaningful, conventional commit message — then commits your code automatically.

No more `"fix"`, `"update"`, or `"changes"`. Every commit in your history will be clear, descriptive, and professional.

### ✨ Key Features

- 🧠 **AI-Powered Messages** — Generates conventional commit messages (`feat:`, `fix:`, `refactor:`, etc.) using Google Gemini or OpenAI
- ⚡ **One-Click Commit** — Trigger from the Command Palette or click the status bar icon
- 🚪 **Auto-Commit on Close** — Automatically commits your changes when you close VS Code (configurable)
- 📊 **Smart Diff Analysis** — Analyzes both staged and unstaged changes to understand what you changed
- 🔒 **Secure** — API keys are passed via environment variables, never written to disk by the extension
- 🛡️ **Graceful Fallback** — If the API fails, it still commits with a sensible default message

---

## 🚀 Quick Start

### Prerequisites

- **VS Code** v1.110.0 or later
- **Python 3.7+** installed and in your PATH
- **`requests`** Python package (`pip install requests`)
- An **API key** from [Google AI Studio](https://aistudio.google.com/apikey) (Gemini) or [OpenAI](https://platform.openai.com/api-keys)

### Installation

1. Open VS Code
2. Go to the Extensions panel (`Ctrl+Shift+X`)
3. Search for **"Auto-Commit!"**
4. Click **Install**

Or install from the terminal:
```bash
code --install-extension PraveenSingh13.auto-commit13
```

### Setup

1. Open VS Code Settings (`Ctrl+,`)
2. Search for **"AutoCommit"**
3. Enter your **API Key**
4. Choose your **AI Provider** (`gemini` or `openai`)
5. You're ready to go! 🎉

---

## 🎯 Usage

### Manual Trigger
1. Make changes to your code
2. Open Command Palette (`Ctrl+Shift+P`)
3. Type **"AutoCommit: Generate & Commit"**
4. Watch the progress spinner — your code is committed with an AI-generated message!

### Status Bar
Click the **$(git-commit) AutoCommit** icon in the bottom status bar to trigger a commit instantly.

### Auto-Commit on Close
By default, Auto-Commit will automatically commit your changes whenever you close the VS Code window. You can disable this in settings:
```
autocommit.commitOnClose: false
```

---

## ⚙️ Configuration

All settings are available in the VS Code Settings UI under **AutoCommit**, or in your `settings.json`:

| Setting | Type | Default | Description |
|---|---|---|---|
| `autocommit.apiKey` | `string` | `""` | Your AI provider API key |
| `autocommit.apiProvider` | `enum` | `"gemini"` | AI provider: `gemini` or `openai` |
| `autocommit.model` | `string` | `"gemini-2.0-flash"` | Model name (e.g., `gemini-2.0-flash`, `gpt-4o-mini`) |
| `autocommit.pythonPath` | `string` | `"python"` | Path to your Python executable |
| `autocommit.commitOnClose` | `boolean` | `true` | Auto-commit when VS Code closes |

### Example `settings.json`

```json
{
  "autocommit.apiKey": "your-api-key-here",
  "autocommit.apiProvider": "gemini",
  "autocommit.model": "gemini-2.0-flash",
  "autocommit.commitOnClose": true
}
```

### Alternative: Config File

You can also configure via `config/config.json` in the extension directory (see `config/config.example.json` for the template). VS Code settings take priority over the config file.

---

## 🏗️ How It Works

```
┌─────────────────────────┐
│  VS Code Extension (JS) │
│  Command / Close Event  │
└───────────┬─────────────┘
            │  spawns
            ▼
┌─────────────────────────┐
│  Python Pipeline        │
│  main.py                │
└───────────┬─────────────┘
            │
  ┌─────────┴─────────┐
  ▼                   ▼
┌──────────┐  ┌──────────────┐
│ git_handler │  │ api_handler   │
│ (subprocess)│  │ (requests)    │
└──────┬───┘  └──────┬───────┘
       │             │
       ▼             ▼
  Git Status      AI API
  Git Diff     (Gemini/OpenAI)
       │             │
       └──────┬──────┘
              ▼
     ┌─────────────────┐
     │  git add .       │
     │  git commit -m   │
     │  "AI message"    │
     └─────────────────┘
```

### Pipeline Steps

1. **Detect** — Checks if you're in a Git repo and if there are uncommitted changes
2. **Analyze** — Fetches `git diff` (staged + unstaged) and current branch name
3. **Generate** — Sends the diff to the AI API with a prompt for conventional commit formatting
4. **Commit** — Stages all changes and commits with the generated message

---

## 📂 Project Structure

```
autoCommit/
├── extension.js              # VS Code extension entry point
├── package.json              # Extension manifest & settings schema
│
├── python/
│   ├── main.py               # Pipeline orchestrator
│   ├── git_handler.py        # Git CLI interactions (subprocess)
│   └── api_handler.py        # AI API calls (Gemini + OpenAI)
│
├── scripts/
│   ├── get_diff.sh           # Shell helper for fetching diffs
│   └── commit.sh             # Shell helper for committing
│
├── config/
│   ├── config.json           # Your local config (gitignored)
│   └── config.example.json   # Template config (safe to commit)
│
└── test/
    └── extension.test.js     # Extension tests
```

---

## 🛡️ Error Handling

| Scenario | What Happens |
|---|---|
| **No Git repo** | Shows an error message: *"Not a git repository"* |
| **No changes** | Shows info: *"No changes detected"* |
| **API failure / timeout** | Falls back to committing with `"update project files"` |
| **Python not found** | Shows error with instructions to install Python or update `pythonPath` |
| **No workspace open** | Shows a warning to open a folder first |
| **Invalid API key** | Falls back to the default commit message |

---

## 🔒 Security

- **API keys** entered in VS Code settings are passed to Python via environment variables — they are never written to a file by the extension
- `config/config.json` is in `.gitignore` to prevent accidentally pushing your API key
- No sensitive code content is logged

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Clone the repo**
   ```bash
   git clone https://github.com/Praveen-Singh13/autoCommit.git
   cd autoCommit
   ```

2. **Install dependencies**
   ```bash
   npm install
   pip install requests
   ```

3. **Run in debug mode**
   - Open the project in VS Code
   - Press `F5` to launch the Extension Development Host
   - Test your changes in the debug window

4. **Lint before pushing**
   ```bash
   npm run lint
   ```

---

## 📅 Roadmap

- [ ] Commit preview window before executing
- [ ] Optional `git push` after commit
- [ ] Branch-aware message patterns
- [ ] Conventional commit format enforcement
- [ ] Local LLM support (Ollama, etc.)
- [ ] Commit history learning

---

## 📄 License

This project is open source. See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Praveen Singh**
- GitHub: [@Praveen-Singh13](https://github.com/Praveen-Singh13)
- VS Code Marketplace: [PraveenSingh13](https://marketplace.visualstudio.com/publishers/PraveenSingh13)

---

<p align="center">
  Made with ❤️ for developers who hate writing commit messages
</p>
