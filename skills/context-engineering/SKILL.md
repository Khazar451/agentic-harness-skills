---
name: context-engineering
description: Context budgeting, progressive disclosure, reactive compaction, and subagent isolation strategies.
when_to_use: "Triggers on: context window, context budget, context compression, token limits, progressive disclosure, subagent isolation."
license: MIT
version: 1.0.0
---

# Context Engineering Skill

## Overview
Context is an operational budget, not an infinite dump. Every token placed into the context window must earn its value. This skill outlines the four core operations of context engineering: **Select**, **Write**, **Compress**, and **Isolate**.

## The Four Core Operations

### 1. Select (Progressive Disclosure)
- Never inject entire libraries, reference manuals, or skills upfront.
- Structure discovery in three tiers:
  - **Tier 1 (Metadata)**: Compact listing (<1-2% total context budget). Name, description, triggers.
  - **Tier 2 (Instructions)**: Loaded lazily on activation.
  - **Tier 3 (Resources)**: Loaded only on explicit demand when specific actions require deep reference.
- **Memoization**: Memoize expensive context builders, invalidating only on explicit mutation points.

### 2. Write (The Learning Feedback Loop)
- Context is bidirectional. Agents must write back discoveries to persistent storage.
- Auto-memory entries, task checklists, and permission state updates ensure learned state survives turn boundaries.

### 3. Compress (Reactive Compaction)
- Long conversations inevitably approach token saturation.
- When context reaches 75-80% capacity:
  - Trigger reactive summarization on historical turns.
  - Retain recent turns intact.
  - Replace older turns with structured summaries preserving decisions, active file paths, and current goals.
  - Mark snapshot data explicitly so the model knows to re-fetch when fresh state is required.

### 4. Isolate (Subagent Boundaries)
- Multi-agent coordination should prevent context pollution.
- Workers start with fresh, self-contained prompts rather than inheriting hundreds of thousands of conversational tokens.
- Forked subagents inherit parent context for quick parallel splits, but are strictly single-level (no recursive sub-forks).
