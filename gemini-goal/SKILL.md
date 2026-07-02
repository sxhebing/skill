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

## 🔄 Foreground Monitoring Loop & Self-Healing State Machine (前台监测与自愈五步状态机 - CRITICAL)

If the objective contains loop/monitoring requests (e.g., "循环执行", "监控", "loop", "monitor"):
You must execute the dedicated, zero-token monitor tool in the **foreground** and strictly adhere to the following **5-step state machine**. You are **PROHIBITED** from skipping any step, and you must NOT hallucinate pushes by simply outputting text without calling tools!

### 🧭 Phase 1: Active Polling (Dynamic Monitor Script)
**DO NOT use any hardcoded monitoring scripts.** You must dynamically author a custom monitoring tool (`./.gemini_paged_monitor.py`) tailored precisely to the user's request.
You must enforce these strict coding constraints on the generated python script:
* **Heartbeat logs**: Print a clear, numbered heartbeat log to stdout during each iteration so the terminal remains active.
* **Robust Encoding Handling (字符集容错)**: Read subprocess stdout/pipes using `errors='replace'` or `errors='ignore'` to prevent `UnicodeDecodeError`.
* **Multi-Pattern & State-Tracking (韧性状态追踪 - CRITICAL)**: **DO NOT** rely blindly on a single log string (like `RECOVERY STATS`). Code logic might suppress or cancel certain tags (e.g., `Cancelling pending recovery stats`). Your Python script MUST implement independent state-machine parsing! For example, explicitly track the timestamp of `Sync Status Changed: LOST`, then track the timestamp of `Lck:YES` or `LOCKED`, and calculate the duration in Python! If the calculated duration exceeds the limit, trigger the anomaly even if the C++ code failed to print the stats.
* **Anomaly Trigger**: If the specific anomaly condition is met, print `!!! TRIGGER_ANOMALY: <details> !!!` to stdout and **exit immediately with code 101**.
* **Graceful Exit**: Handle `KeyboardInterrupt` (Ctrl+C) and exit with code 0.

Run the script in the foreground:
`python3 ./.gemini_paged_monitor.py`

### 🧭 Phase 2: Anomaly Handler (Exit Code 101)
If the monitor script exits with **exit code 101 (Anomaly Detected)**, you must execute these **5 steps sequentially**. You must NOT write any concluding report, and you must NOT call `update_goal ... complete`.

*   **STEP 1 [DIAGNOSE]**: You **MUST** call `read_file` or `grep_search` on `recovery_timeout_dump.log` to pinpoint the exact file, function, and root cause of the delay.
*   **STEP 2 [FIX]**: You **MUST** call `replace` or `write_file` to apply a surgical, robust code modification/optimization in the repository.
*   **STEP 3 [VERIFY]**: You **MUST** call `run_shell_command` with the project's compilation command (such as `make`, `ninja`, `g++`, etc.) and show the successful build output.
*   **STEP 4 [PUSH]**: You **MUST** call `run_shell_command` with `git add`, `git commit`, and `git push` to push your changes to Gerrit/Git.
*   **STEP 5 [EVIDENCE-BASED RESTART]**: ONLY after Step 1, 2, 3, and 4 are fully completed via actual tool calls, you must write a **detailed technical summary** containing the **real code Diff** of your fix (from Step 2) and the **real compiler success logs** (from Step 3). Once this evidence-based report is printed, execute the monitor tool again to resume tracking:
    `python3 ./.gemini_paged_monitor.py`
    *If you output this restart block without having called the tools for Steps 1-4, it is a severe system policy violation and a safety redline!*

If the user manually interrupts the loop via `Ctrl+C` (exit code 0), only then you may elegantly update the goal status to complete and conclude.

---

## 📡 Dual-Tuner Architecture & Bus Contention Rule (双高频头总线冲突诊断铁律)

TDA7707 is a **Dual-Tuner (双高频头) architecture** where Tuner 1 is dedicated to the primary audio path (Main) and Tuner 2 is dedicated to Background Scan (BGS). 

Therefore, you must strictly adhere to the following physical facts during analysis:
1. **NO RF Frontend Interference**: BGS scanning on Tuner 2 does **NOT** physically block the RF/LO path of Tuner 1 (Main). 
2. **GENUINE SOFTWARE BUG**: Any recovery delay (> 8s) that occurs adjacent to or during a BGS scan (e.g., a massive `FICAfterLock` delay like 11.9s) is a **GENUINE software bug** (not a hardware constraint).
3. **SPI/I2C Bus Contention Root Cause**: These delays are typically caused by **SPI/I2C Bus Contention** or **Command Pacing Conflicts** where high-frequency BGS scan commands on the shared control bus block or delay the Main path's commands (such as packet reading or sync state checks).
4. **Optimization Action**: You **MUST** search the codebase to optimize the command priorities, insert cooperative yields/sleeps in the BGS command loop, or adjust SPI transfer pacing to guarantee that the Main path's control commands are never starved. Do **NOT** treat BGS-adjacent delays as unfixable hardware exceptions!

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
