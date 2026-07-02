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

### 🧭 Phase 1: Active Polling
- Run the following command in the foreground:
  `python3 ~/.agents/skills/gemini-goal/scripts/monitor.py`
- This script runs the loop and prints heartbeats. No tokens are consumed during successful checks.

### 🧭 Phase 2: Anomaly Handler (Exit Code 101)
If the monitor script exits with **exit code 101 (Anomaly Detected)**, you must execute these **5 steps sequentially**. You must NOT write any concluding report, and you must NOT call `update_goal ... complete`.

*   **STEP 1 [DIAGNOSE]**: You **MUST** call `read_file` or `grep_search` on `recovery_timeout_dump.log` to pinpoint the exact file, function, and root cause of the delay.
*   **STEP 2 [FIX - C++ 源码修改刚性约束]**: You **MUST** call `replace` or `write_file` to apply a surgical, robust code modification/optimization in the **C++ source files (such as .cpp, .h, .c)**. **You are strictly FORBIDDEN from modifying monitor script thresholds or Python scripts to "bypass" the anomaly. You must optimize the actual C++ driver code!**
*   **STEP 3 [VERIFY]**: You **MUST** call `run_shell_command` with the project's compilation command (such as `make`, `ninja`, `g++`, etc.) and show the successful build output.
*   **STEP 4 [PUSH]**: You **MUST** call `run_shell_command` with `git add`, `git commit`, and `git push` to push your changes to Gerrit/Git.
*   **STEP 5 [EVIDENCE-BASED RESTART]**: ONLY after Step 1, 2, 3, and 4 are fully completed via actual tool calls, you must write a **detailed technical summary** containing the **real code Diff** of your C++ fix (from Step 2) and the **real compiler success logs** (from Step 3). Once this evidence-based report is printed, execute the monitor tool again to resume tracking:
    `python3 ~/.agents/skills/gemini-goal/scripts/monitor.py`
    *If you output this restart block without having called the tools for Steps 1-4 to edit C++ files, it is a severe system policy violation and a safety redline!*

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

---

## 🚨 The Blocked Audit (阻塞定义准则)

Do not call `update_goal ... blocked` the first time an error or blocker appears!

1. **The 3-Turn Try Principle (三击不中原则)**: You must attempt to solve the blocker using at least **3 consecutive turns of different strategies** (such as looking for different files, compiling with alternative flags, or fixing local environments via `env_doctor.py`).
2. **True Impasse**: Only set the status to `blocked` when you are at a complete dead-end and cannot make any progress without user-provided details or external state changes.
3. **Never Block on Difficulty**: Never mark a goal `blocked` merely because the task is slow, difficult, uncertain, or could benefit from some casual clarification.
