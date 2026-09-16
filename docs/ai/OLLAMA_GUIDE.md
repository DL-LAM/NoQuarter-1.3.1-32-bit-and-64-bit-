# Complete Guide: Installing and Using the `nq-dev` Local AI Assistant

> **Target Audience**: Developers, server administrators, and modders working on NoQuarter 1.3.1.  
> **Privacy & Offline Status**: 100% Offline, Local Execution. No telemetry, no subscriptions, no external APIs required.

---

## Table of Contents
1. [Overview](#1-overview)
2. [System Requirements & Hardware Recommendations](#2-system-requirements--hardware-recommendations)
3. [Installing Ollama](#3-installing-ollama)
4. [Building the `nq-dev` Model](#4-building-the-nq-dev-model)
5. [Interactive Terminal Usage & Commands](#5-interactive-terminal-usage--commands)
6. [Tuning for Your Hardware (Model Options)](#6-tuning-for-your-hardware-model-options)
7. [In-Editor Integration with VS Code (Continue.dev)](#7-in-editor-integration-with-vs-code-continuedev)
8. [Local Graphical Web UI (ChatGPT-Style Interface)](#8-local-graphical-web-ui-chatgpt-style-interface)
9. [Full Codebase Indexing (Local RAG)](#9-full-codebase-indexing-local-rag)
10. [Sample NoQuarter Prompts & Scenarios](#10-sample-noquarter-prompts--scenarios)
11. [FAQ & Troubleshooting](#11-faq--troubleshooting)

---

## 1. Overview

Working on 15- to 20-year-old game engines like *Wolfenstein: Enemy Territory* (id Tech 3) is notoriously challenging. Legacy mod codebases—such as historical NoQuarter 1.2.9 and earlier community patches—often contain cryptic pointer castings, unwritten networking rules, and fragile rendering quirks.

To prevent future contributors from getting stuck or repeating past mistakes, this repository packages **`nq-dev`**: a specialized local AI development assistant pre-configured with:
* Full knowledge of the **32-bit and 64-bit dual architecture** and universal PK3 layout.
* Lessons learned from real bugfixes (e.g. 10-frame airstrike propeller animations, 32-bit CMYK texture engine crashes, and HUD coordinate collisions).
* Strict adherence to **safe C programming standards** (`Q_strncpyz`, struct packing, memory pools).
* Server CVAR registration patterns and Lua 5.1 API hooks.

---

## 2. System Requirements & Hardware Recommendations

`nq-dev` runs locally using **Ollama**, an open-source tool that executes Large Language Models directly on your CPU or GPU.

| Component | Minimum | Recommended | High-End Workstation |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 (64-bit), Linux, macOS | Windows 10/11 (64-bit), Linux | Windows 11 / Linux |
| **RAM** | 8 GB System RAM | 16 GB System RAM | 32 GB+ System RAM |
| **GPU (VRAM)** | None (Runs on CPU via AVX2) | 4 GB – 8 GB VRAM | 12 GB – 16 GB+ Dedicated VRAM |
| **Disk Space** | ~5 GB free space | ~8 GB free space | ~15 GB free space |
| **Default Model** | `qwen2.5-coder:7b` (Q4) | `qwen2.5-coder:7b` (Q4) | `qwen2.5-coder:14b` or `deepseek-coder-v2` |

> [!NOTE]
> Even without a high-end gaming GPU, modern CPUs with AVX/AVX2 instruction sets run `qwen2.5-coder:7b` at smooth, readable speeds (15–30 tokens per second).

---

## 3. Installing Ollama

### Windows:
1. Download the official installer: **[https://ollama.com/download/OllamaSetup.exe](https://ollama.com/download/OllamaSetup.exe)**
2. Run `OllamaSetup.exe` and complete the wizard.
3. Ollama runs silently in your Windows System Tray (near the clock).

> [!IMPORTANT]
> **New Terminal Required**: If you already had PowerShell or Command Prompt open before installing, **close and reopen it** so Windows loads the new `PATH` environment variable.

Verify installation by running:
```powershell
ollama --version
```
If you see something like `ollama version is 0.5.x` (or newer), Ollama is ready.

### Linux:
Open terminal and run:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS:
Download the `.zip` archive from [https://ollama.com/download/mac](https://ollama.com/download/mac), unzip, and drag Ollama to your Applications folder.

---

## 4. Building the `nq-dev` Model

The repository provides a pre-configured `Modelfile` inside `docs/ai/` that bundles the code-generation model with NoQuarter 1.3.1's architectural knowledge base.

### Step 1: Open PowerShell and navigate to the repository
```powershell
cd "C:\Users\Dylan\Documents\ETFiles\WET-NoQuarter-master\NQV1.3.0dev\trunk\NoQuarter-v1.3.1-Source\docs\ai"
```

### Step 2: Build the model
```powershell
ollama create nq-dev -f Modelfile
```

#### What happens during this command:
1. **Pulls Base Weights**: Downloads the `qwen2.5-coder:7b` foundation weights (~4.7 GB). (If you have already pulled it, this step is instantaneous).
2. **Injects System Prompt**: Injects the NoQuarter architecture rules, memory constraints, and CVAR specifications into the model's core context.
3. **Compiles Model Manifest**: Registers `nq-dev` into your local Ollama library.

---

## 5. Interactive Terminal Usage & Commands

To start an interactive chat session in your terminal:
```powershell
ollama run nq-dev
```

You will be greeted with the interactive prompt:
```text
>>> Send a message (/? for help)
```

### Essential In-Chat Commands:
* **`/bye`** or **`Ctrl + D`**: Exit the chat and return to PowerShell.
* **`"""` (Multi-line Code Input)**: If you want to paste multiple lines of C code or a crash dump, type `"""`, hit Enter, paste your code, type `"""` on a new line, and hit Enter.
* **`/clear`**: Wipes the active conversation memory so you can start a new, unrelated task with fresh context.
* **`/set verbose`**: Toggles generation metrics (displays tokens-per-second speed and memory usage after each response).
* **`/show info`**: Displays the model's active parameters, template, and system instructions.

---

## 6. Tuning for Your Hardware (Model Options)

The default `Modelfile` specifies `FROM qwen2.5-coder:7b`. You can easily swap the base model to match your computer's specifications by editing the first line of `Modelfile`:

### For Lighter / Older Laptops (4 GB – 8 GB RAM):
Edit line 1 of `Modelfile`:
```dockerfile
FROM qwen2.5-coder:3b
```
Then run `ollama create nq-dev -f Modelfile`. This version uses only ~2 GB of memory and generates answers instantaneously.

### For Powerful Workstations (16 GB+ VRAM / 32 GB+ RAM):
Edit line 1 of `Modelfile`:
```dockerfile
FROM qwen2.5-coder:14b
```
or
```dockerfile
FROM deepseek-coder-v2:16b
```
Then rebuild. The 14B model provides deeper multi-file refactoring reasoning and advanced C pointer analysis.

---

## 7. In-Editor Integration with VS Code (Continue.dev)

You can turn `nq-dev` into a private, offline replacement for GitHub Copilot directly inside Visual Studio Code.

### Step 1: Install the Continue Extension
1. In VS Code, open the Extensions view (`Ctrl + Shift + X`).
2. Search for **Continue** (by *Continue*) and click **Install**.

### Step 2: Configure Continue for `nq-dev`
1. Open the Continue settings by clicking the gear icon at the bottom of the Continue sidebar, or edit `~/.continue/config.json`.
2. Add `nq-dev` to the `models` list:
   ```json
   {
     "models": [
       {
         "title": "NoQuarter Dev Assistant (Local)",
         "provider": "ollama",
         "model": "nq-dev"
       }
     ],
     "tabAutocompleteModel": {
       "title": "Autocomplete",
       "provider": "ollama",
       "model": "qwen2.5-coder:1.5b"
     }
   }
   ```

### Step 3: Coding Shortcuts
* **`Ctrl + I` (Inline Edit)**: Highlight any function in `g_weapon.c` or `cg_draw.c`, press `Ctrl + I`, and prompt: *"Add rate-of-fire check based on skill level"*.
* **`Ctrl + L` (Chat with File Context)**: Opens the sidebar chat with the currently active file automatically attached.

---

## 8. Local Graphical Web UI (ChatGPT-Style Interface)

If you prefer a clean web interface in your browser instead of a terminal:

### Option A: Page Assist (Browser Extension - Fastest Setup)
1. Install **Page Assist** from the Chrome Web Store or Firefox Add-ons.
2. Click the extension icon in your toolbar.
3. Select `nq-dev` from the dropdown menu and start chatting. It runs 100% locally through your existing Ollama service.

### Option B: OpenWebUI (Full Self-Hosted Suite)
If you have Docker installed:
```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```
Open `http://localhost:3000` in your web browser.

---

## 9. Full Codebase Indexing (Local RAG)

Want `nq-dev` to read, search, and cite exact line numbers across all 1,400+ files in `NoQuarter-v1.3.1-Source`?

1. Install **[AnythingLLM](https://useanything.com/)** (free, local desktop app).
2. Under Settings $\rightarrow$ AI Providers:
   * **LLM Provider**: Choose **Ollama** $\rightarrow$ select `nq-dev`.
   * **Embedding Provider**: Choose **Ollama** $\rightarrow$ select `nomic-embed-text` (Ollama will pull this 250 MB model automatically).
3. Create a workspace named `NoQuarter`.
4. Drag and drop the `NoQuarter-v1.3.1-Source/src/` folder into AnythingLLM and click **Send to Workspace**.
5. You now have a searchable local vector database. You can ask:
   > *"Find all occurrences of `g_soldierShotgun` across the entire codebase and show which files check it."*

---

## 10. Sample NoQuarter Prompts & Scenarios

### Scenario 1: Adding a Server CVAR
> **Prompt**:  
> *"I want to create a new server cvar named `g_artilleryCooldown` that adjusts the recharge time for Field Ops artillery. Show me the declaration in `g_local.h`, registration in `g_main.c`, and where to apply it in `g_weapon.c`."*

### Scenario 2: Debugging UI / Menu Glitches
> **Prompt**:  
> *"The center screen kill announcement text is overlapping the left kill popup messages on my custom HUD. What coordinate floor and font should I enforce in `cg_draw.c` to fix this?"*

### Scenario 3: Modifying Weapons
> **Prompt**:  
> *"Explain how secondary weapon selection works in the Limbo menu for Soldiers who unlock Heavy Weapons level 4, and how to prevent the secondary weapon from overriding the primary weapon upon spawn."*

### Scenario 4: Cross-Architecture Safety
> **Prompt**:  
> *"I need to pass custom player statistics from the server to the client. Why shouldn't I put a raw pointer inside `playerState_t`, and what should I do instead?"*

---

## 11. FAQ & Troubleshooting

### Q: `ollama : The term 'ollama' is not recognized`
* **Cause**: You are using a terminal window that was opened before the Ollama installer completed.
* **Fix**: Close all PowerShell / Command Prompt windows and open a new one.

### Q: `Error: pull model manifest: connection refused`
* **Cause**: The Ollama background service is not running.
* **Fix**: Look for the Ollama llama icon in your Windows System Tray, or search for "Ollama" in the Start Menu and launch it.

### Q: How do I free up RAM after using the model?
* Run:
  ```powershell
  ollama stop nq-dev
  ```
  This immediately unloads the model weights from your system memory / VRAM.

### Q: How do I update `nq-dev` after modifying the C code or docs?
* Simply re-run:
  ```powershell
  ollama create nq-dev -f Modelfile
  ```
  It will recompile the model using your updated instructions in seconds.
