# Gemini-Goal Agent Skill 🎯

Provides structured long-term goal management for Gemini CLI / Codex. Enforces a rigorous **Completion Audit** and **Blocked Audit** framework to prevent premature task termination and guarantee objective verification.

## 📦 Installation

To install this skill globally in your Gemini CLI configuration:

1. Clone or download this repository.
2. Place it under your global personal skills directory:
   ```bash
   mkdir -p ~/.agents/skills/gemini-goal
   # Copy SKILL.md and scripts directory
   cp -r * ~/.agents/skills/gemini-goal/
   ```

## ⚡ How to Use

Simply start your prompt in Gemini CLI with the `/gemini-goal` prefix:

```bash
/gemini-goal Implement a new robust feature and verify with unit tests
```

Gemini CLI will semantically route your request to the `gemini-goal` skill, automatically initialize the goal state manager in the background, and execute your goal under strict verification audits!