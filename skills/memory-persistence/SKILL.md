---
name: memory-persistence
description: Multi-layered agent memory patterns with two-step save invariants, auto-memory indexing, and session extraction.
when_to_use: "Triggers on: agent memory, persistent memory, cross-session recall, auto-memory, memory indexing, session learning."
license: MIT
version: 1.0.0
---

# Memory Persistence Pattern Skill

## Overview
When agents interact across sessions or operate over extended tasks, they risk losing context, user corrections, and project conventions. This skill provides explicit architectural patterns for implementing multi-layer persistent agent memory.

## The Three Memory Layers

1. **Instruction Memory (Hierarchical & Curated)**
   - Injected into system context in strict priority: `org-wide` -> `user` -> `project` -> `local` (`local` wins).
   - Contains coding standards, user preferences, and stable behavioral rules.
   - Author: Human user or explicitly approved promotions.

2. **Auto-Memory (Agent-Written Persistent Knowledge)**
   - Topic-based entries categorized by type:
     - `user`: Personal preferences and workflow quirks.
     - `feedback`: Corrections or explicit instructions given during turns.
     - `project`: Architecture decisions, dependency notes, and conventions.
     - `reference`: Key URLs, paths, commands, or data formats.
   - Subject to a capped index: Old or low-frequency memories are evicted or consolidated.

3. **Session Extraction (Background Learning Loop)**
   - Runs asynchronously at session completion.
   - Scans the session transcript for reusable insights and updates auto-memory without human interruption.

## The Two-Step Save Invariant

> [!IMPORTANT]
> Never write directly to the memory index without persisting the topic file first!

Whenever writing or updating auto-memory:
1. **Step 1 (Write Topic File)**: Write the detailed knowledge into `memory/<category>/<topic-slug>.md`.
2. **Step 2 (Update Index)**: Update the central `memory/INDEX.md` with a one-line summary and relative link.

If an operation fails between Step 1 and Step 2, the topic file remains readable and no broken index references are created.

## Anti-Patterns to Avoid
- **Unbounded Index Growth**: Memory indexes without caps cause context bloat. Cap indexes at ~50 entries.
- **Direct Autonomous Edits to Instruction Memory**: Auto-memory should propose promotions to instruction memory, never overwrite human-curated instructions directly without confirmation.
- **Race Conditions in Session Extraction**: Ensure mutual exclusion guards so background extraction does not overwrite concurrent turn edits.
