---
name: gemini-goal
description: Provides structured long-term goal management for Gemini CLI. TRIGGERED immediately when the user prompt starts with '/gemini-goal <objective>' or mentions '/gemini-goal'. This skill enforces a rigorous Completion Audit and Blocked Audit framework to prevent premature termination and guarantee objective verification.
license: MIT
---

# Gemini Goal Management Skill (gemini-goal)

**Goal-Driven Execution** is a framework that forces the AI agent to turn abstract user tasks into structured, verifiable long-term goals.

---

## ⚡ Slash Command Activation Rules (命令激活规则)

If the user prompt starts with or contains `/gemini-goal <objective>`:
1. **Immediate Setup**: You must IMMEDIATELY run:
   `python3 ~/.agents/skills/gemini-goal/scripts/goal.py create "<objective>"`
   to register the goal in the system state.
2. **Confirm Activation**: Acknowledge the goal initialization, display the goal summary, and present your requirement-by-requirement plan.
3. **Audit Execution**: Pursue this objective using the Plan-Act-Validate loop under the Completion Audit rules below.

---

## 🔄 Foreground Monitoring Loop (前台循环监测机制 - 0 Token 挂载)

If the objective contains loop/monitoring requests (e.g., "循环执行", "监控", "loop", "monitor"):
You must execute the dedicated, zero-token monitor tool in the **foreground** inside the same session:

1. **Launch the Foreground Monitor**:
   - Run the following command:
     `python3 ~/.agents/skills/gemini-goal/scripts/monitor.py`
   - This script runs an active loop in the foreground, printing heartbeats to stdout so the session remains active and alive without hitting idle timeouts.
   - While the tool is running, **no tokens are consumed** during successful checks, keeping the session efficient.

2. **Handle the Monitor Exit Code**:
   - **Case A (Exit Code 101 - Anomaly Detected)**: If `monitor.py` exits with code 101, it means recovery duration exceeded 8 seconds and the logs are dumped to `recovery_timeout_dump.log`. 
     You must **IMMEDIATELY** start the deep self-healing cycle in the same session:
     - Read the logs in `recovery_timeout_dump.log` to locate the root cause.
     - Surgical-edit the source code to optimize/fix the issue.
     - Verify the build and run any tests.
     - Push the package/Gerrit change.
     - **CRITICAL**: After the successful push, do NOT mark the goal complete! **Immediately re-run** `python3 ~/.agents/skills/gemini-goal/scripts/monitor.py` to resume the loop!
   - **Case B (Exit Code 0 - Stopped by User)**: If the user manually interrupts the loop via `Ctrl+C`, update the goal status and elegantly conclude.

---

## 🛠️ State Management Tools

This skill exposes local CLI tools to manage goal states via `~/.agents/skills/gemini-goal/scripts/goal.py`. 
You must execute these tools via `run_shell_command` when managing goal states:

1. **Create Goal**:
   `python3 ~/.agents/skills/gemini-goal/scripts/goal.py create "<objective>" [token_budget]`
   *Use only when explicitly requested to start a long-term goal. Do not create goals for simple queries.*

2. **Get Current Goal**:
   `python3 ~/.agents/skills/gemini-goal/scripts/goal.py get`
   *Use to check active goal requirements, elapsed progress, and current state.*

3. **Update Goal**:
   `python3 ~/.agents/skills/gemini-goal/scripts/goal.py update <complete|blocked|active> "[reason]" [token_increment]`
   *Use to mark goals complete or blocked according to strict audits.*

---

## 🔍 The Rigorous Completion Audit (完成审计准则)

Before calling `update_goal ... complete` to mark a goal as achieved, you **MUST** treat completion as unproven and perform a strict verification check against the actual current state:

1. **Derive Concrete Requirements**: Break down the overall objective into clear, testable, requirement-by-requirement items.
2. **Authorize Evidence Only**: Do not rely on "intent", "partial progress", "expected outputs", or "confidence". You must prove completion via **authoritative current-state evidence**:
   - Files exist and contain the correct content.
   - Local unit tests or builds pass successfully.
   - Command line verification yields correct exits.
3. **No Drive-by Assumptions**: The audit must prove absolute completion, not merely fail to find obvious remaining bugs.
4. **Conclusion**: Only mark complete once current evidence proves every requirement has been 100% satisfied.

---

## 🚨 The Blocked Audit (阻塞定义准则)

Do not call `update_goal ... blocked` the first time an error or blocker appears!

1. **The 3-Turn Try Principle (三击不中原则)**: You must attempt to solve the blocker using at least **3 consecutive turns of different strategies** (such as looking for different files, compiling with alternative flags, or fixing local environments via `env_doctor.py`).
2. **True Impasse**: Only set the status to `blocked` when you are at a complete dead-end and cannot make any progress without user-provided details or external state changes.
3. **Never Block on Difficulty**: Never mark a goal `blocked` merely because the task is slow, difficult, uncertain, or could benefit from some casual clarification.
