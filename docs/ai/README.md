# Offline AI Developer Assistant for NoQuarter 1.3.1

This directory contains configuration blueprints to create a **100% offline, localized AI assistant** (`nq-dev`) customized for the NoQuarter 1.3.1 codebase.

With this setup, future developers or server administrators can troubleshoot issues, write new CVARs, analyze crash dumps, and extend the mod completely offline without an internet connection or external API keys.

---

## 🚀 Quick Start (Using Ollama)

### Step 1: Install Ollama
Download and install Ollama for your operating system:
* **Windows / macOS / Linux**: [https://ollama.com/download](https://ollama.com/download)

Verify installation in PowerShell or Terminal:
```bash
ollama --version
```

---

### Step 2: Build the Local `nq-dev` Model
Navigate to this directory (`docs/ai/`) and build the customized assistant:

```bash
cd docs/ai
ollama create nq-dev -f Modelfile
```

> **Note**: This will automatically pull the high-performance base model `qwen2.5-coder:7b` (approximately 4.7 GB) and bundle it with NoQuarter's engine rules, architecture constraints, and bugfix history.
> If your workstation has $\ge 16$ GB of VRAM, you can edit `Modelfile` to use `FROM qwen2.5-coder:14b` or `FROM deepseek-coder-v2:16b` for even deeper reasoning.

---

### Step 3: Run and Chat with the Assistant
Launch the assistant interactively in your terminal:

```bash
ollama run nq-dev
```

You can now ask questions directly:
* *"How do I add a new server CVAR to control weapon recoil?"*
* *"Why is the 32-bit client crashing on a custom map texture?"*
* *"Where is the Limbo menu secondary weapon auto-equip logic located?"*
* *"How do I compile the 64-bit cgame DLL with CMake?"*

Type `/bye` to exit.

---

## 💻 Integrating with VS Code / Continue.dev (In-IDE Copilot)

To use your local `nq-dev` model directly inside VS Code (like GitHub Copilot, but 100% offline and free):

1. Install the **Continue** extension from the VS Code Marketplace (`Continue.continue`).
2. Open the Continue settings (`~/.continue/config.json`) and add your local model:
   ```json
   {
     "models": [
       {
         "title": "NoQuarter Dev Assistant",
         "provider": "ollama",
         "model": "nq-dev"
       }
     ]
   }
   ```
3. Highlight any C code in `src/game/` or `src/cgame/` and press `Ctrl+I` (or `Cmd+I`) to ask your local assistant to debug, refactor, or explain it with full codebase context!

---

## 🔍 Full Codebase Indexing (Local RAG)

If you want the model to automatically read and quote exact lines from every file across `src/`:
1. Use **AnythingLLM** ([https://useanything.com/](https://useanything.com/)) or **Continue.dev** @codebase feature.
2. Point AnythingLLM to Ollama (`http://localhost:11434`) as the LLM provider, and select `nomic-embed-text` as the embedder.
3. Import the `NoQuarter-v1.3.1-Source` folder.
4. It will vectorize all `.c`, `.h`, `.cfg`, `.menu`, and `.shader` files locally on your machine.
