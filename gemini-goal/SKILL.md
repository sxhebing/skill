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

## 🔄 Foreground Monitoring Loop (前台循环检测模式)

If the objective contains loop/monitoring requests (e.g., "循环执行", "监控", "loop", "monitor"):
**DO NOT** run a background process that hides output from the user, and **DO NOT** run an infinite bash loop that hangs forever without yielding.

Instead, you must adopt the **Active Foreground Polling Pattern (前台轮询唤醒机制)**:

1. **Write a Paged Monitor Script** (e.g., `gemini_paged_monitor.sh`):
   - The script runs a loop for a fixed number of iterations (e.g., 20-30 iterations, sleeping 3 seconds per check).
   - In each iteration, it **MUST print a heartbeat log** to stdout (e.g., `[Check 1/30] Recovery: 4210ms`) so that the terminal stays alive and does not trigger idle timeouts.
   - If the trigger condition is met (e.g., recovery duration > 8000ms), the script must print a clear trigger token: `!!! TRIGGER_ANOMALY: <details> !!!` and **exit immediately with code 0**.
   - If the paged iterations finish without any trigger, exit with code 99 (No anomaly found in this page).

2. **Execute the Script in the Foreground**:
   - Call `run_shell_command` to execute the script in the **foreground** (do NOT use `is_background: true`).
   - The user will see the heartbeat output and know the skill is actively executing the loop.

3. **Handle the Tool Return**:
   - **Case A (Triggered)**: If the tool output contains `TRIGGER_ANOMALY`, immediately transition to the **Analysis, Fix, and Push** phase within the same conversational turn! Read the dumped logs, locate the root cause, edit the source code, verify, and push.
   - **Case B (No Anomaly)**: If the script exits with code 99 (no anomaly found), write a brief thought explaining that the current check cycle is clean, and **immediately run the tool again** to start the next polling page. This keeps the loop active within the execution of the skill itself!

---

## ♾️ Persistent Monitoring Goals (持续性监控原则)

If the user objective implies **continuous, non-stop loop execution** (e.g., "循环检测时长...优化代码并推包" which should run indefinitely even after a bug is found and fixed):
1. **Do NOT Complete the Goal**: After you successfully locate a timeout, optimize the code, run your verification, and push the package/Gerrit change, **DO NOT** mark the goal complete and exit!
2. **Resume the Monitoring Loop**: Instead, treat the push as an intermediate milestone. Output a brief triumph message to the user, and then **immediately call the monitor tool again** to resume monitoring the newly pushed build. 
3. **Maintained Execution**: This keeps the agent active forever in a loop of [Monitor ➔ Catch ➔ Fix ➔ Push ➔ Resume Monitor], providing true continuous integration and regression testing.

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
