# My AI Agent Skills 🎯

A collection of custom, highly optimized skills for Gemini CLI / Codex. These skills extend the agent's capabilities with specialized workflows, state machines, and tools.

## 📦 Available Skills

*   **[gemini-goal](./skills/gemini-goal)**: Provides structured, long-term goal management for Gemini CLI. Enforces a rigorous **Completion Audit** and **Blocked Audit** framework to prevent premature task termination and guarantee objective verification. Supports loop execution and recursive background monitoring natively.

## 📥 Installation

To install any of the skills globally in your Gemini CLI environment:

1. Clone or download this repository.
2. Create your global skills directory if it doesn't exist:
   ```bash
   mkdir -p ~/.agents/skills/
   ```
3. Copy the specific skill directory from this repo (e.g. `skills/gemini-goal/`) to your global path:
   ```bash
   cp -r skills/gemini-goal/ ~/.agents/skills/gemini-goal/
   ```

## 🚀 Future Additions

This repository is structured to support multiple skills. More advanced workflows, developer templates, and automations will be added here in their respective subfolders under `skills/`!