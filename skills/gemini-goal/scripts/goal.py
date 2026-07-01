#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex-style Goal State Manager for Gemini CLI.
"""
import os
import sys
import json
import datetime

GOAL_FILE = ".gemini_goal.json"

def load_goal():
    if os.path.exists(GOAL_FILE):
        try:
            with open(GOAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_goal(goal_data):
    with open(GOAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(goal_data, f, ensure_ascii=False, indent=2)

def create_goal(objective, token_budget=None):
    goal = load_goal()
    if goal and goal.get("status") == "active":
        print(json.dumps({
            "status": "error",
            "message": "Cannot create a new goal because this thread has an unfinished active goal. Complete or block the existing goal first."
        }, ensure_ascii=False))
        sys.exit(1)
    
    new_goal = {
        "objective": objective,
        "status": "active",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "token_budget": int(token_budget) if token_budget else None,
        "tokens_used": 0,
        "blocked_count": 0,
        "requirements": []
    }
    save_goal(new_goal)
    print(json.dumps({
        "status": "success",
        "message": "Goal created successfully.",
        "goal": new_goal
    }, ensure_ascii=False))

def get_goal():
    goal = load_goal()
    if not goal:
        print(json.dumps({
            "status": "empty",
            "message": "No active goal found in this workspace."
        }, ensure_ascii=False))
        return
    print(json.dumps({
        "status": "success",
        "goal": goal
    }, ensure_ascii=False))

def update_goal(status, reason=None, tokens_used_increment=0):
    goal = load_goal()
    if not goal:
        print(json.dumps({
            "status": "error",
            "message": "Cannot update goal because no goal exists."
        }, ensure_ascii=False))
        sys.exit(1)
        
    if status not in ["complete", "blocked", "active"]:
        print(json.dumps({
            "status": "error",
            "message": "Invalid status. Allowed: complete, blocked, active"
        }, ensure_ascii=False))
        sys.exit(1)
        
    goal["status"] = status
    goal["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if tokens_used_increment:
        goal["tokens_used"] = goal.get("tokens_used", 0) + int(tokens_used_increment)
        
    if status == "blocked":
        goal["blocked_count"] = goal.get("blocked_count", 0) + 1
        
    if reason:
        goal["last_reason"] = reason

    save_goal(goal)
    print(json.dumps({
        "status": "success",
        "message": f"Goal status updated to '{status}'.",
        "goal": goal
    }, ensure_ascii=False))

def print_help():
    help_text = """
Codex Goal CLI Utility

Usage:
  python3 goal.py create "<objective>" [token_budget]
  python3 goal.py get
  python3 goal.py update <complete|blocked|active> [reason] [tokens_used_increment]
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 3:
            print("Error: Objective is required.")
            sys.exit(1)
        budget = sys.argv[3] if len(sys.argv) > 3 else None
        create_goal(sys.argv[2], budget)
    elif cmd == "get":
        get_goal()
    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Error: Status is required.")
            sys.exit(1)
        status = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        inc = sys.argv[4] if len(sys.argv) > 4 else 0
        update_goal(status, reason, inc)
    else:
        print_help()
