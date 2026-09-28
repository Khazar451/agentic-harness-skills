---
name: tool-permission-guard
description: Fail-closed tool registration, per-call dynamic concurrency classification, and multi-layered permission gating.
when_to_use: "Triggers on: tool safety, permission pipeline, fail-closed, tool concurrency, sandbox bypass, tool approval."
license: MIT
version: 1.0.0
---

# Tool & Permission Safety Guard Skill

## Overview
Autonomous agents executing code and tools on the local machine must balance speed with ironclad safety. This skill specifies the architecture for fail-closed tool management, concurrency segmentation, and permission pipelines.

## Architectural Principles

### 1. Fail-Closed Registration
- By default, every registered tool is considered **mutating**, **serial**, and **requires approval**.
- A tool or call only bypasses confirmation if an explicit whitelist or allow rule matches.
- Never assume an unknown tool is read-only.

### 2. Per-Call Dynamic Concurrency
- Concurrency classification is a property of the **invocation arguments**, not just the tool name.
- Example:
  - `run_command("git status")` is read-only and safe for concurrent execution.
  - `run_command("rm -rf src/")` is mutating and requires serial isolation and explicit user approval.
- Group batched tool calls:
  - Parallel segment: Read-only, safe concurrent calls execute simultaneously.
  - Serial segment: Any mutating call halts batch parallelism and runs alone.

### 3. Layered Permission Evaluation
Evaluate permissions through strict descending precedence:
1. Protected Path Invariants (cannot be bypassed by auto-approve)
2. CLI Flags / Explicit Session Grants
3. Command-scoped Rules
4. Project Configuration (`.gemini/rules`, `.agent/rules`)
5. Global User Configuration (`~/.config/...`)
6. Default Policy: Ask / Deny

## Statefulness in Permission Evaluators
- Permission evaluation is not a pure function:
  - Track denials: Repeated denials should trigger fallback behaviors or backoff.
  - Track session grants: Ephemeral "allow for this session" grants must auto-expire on session termination.
