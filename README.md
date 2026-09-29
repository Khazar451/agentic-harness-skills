# Agentic Harness Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A production-grade harness engine, CLI validator, and curated catalog of reusable skills for AI coding agents.

This project implements the foundational patterns described in **Agentic Harness Patterns** (distilled from production systems like Claude Code and modern autonomous runtimes):
- **Two-Phase Skill Discovery**: Fast metadata scanning under tight token budgets with lazy body activation.
- **Strict Budget & Boundary Enforcement**: Front-loaded trigger matching, description length caps, and prompt bloat prevention.
- **Fail-Closed Permissions & Safety**: Per-call concurrency classification, multi-tiered permission gating.
- **Context Engineering**: Selective loading, progressive disclosure, compression, and subagent isolation.
- **Persistent Agent Memory**: Two-step save invariant (topic file, then index) across instruction, auto, and session layers.

---

## Architecture Overview

```
agentic-harness-skills/
├── src/agentic_harness_skills/   # Core Python Harness Runtime & CLI
│   ├── core/                     # Foundational runtime primitives
│   │   ├── schema.py             # Skill metadata & YAML frontmatter models
│   │   ├── loader.py             # Fast catalog scanner & lazy body loader
│   │   └── runner.py             # Execution dispatcher (inline vs isolated)
│   ├── cli.py                    # CLI interface (list, validate, inspect, benchmark)
│   └── patterns/                 # Reference harness implementations
├── skills/                       # Curated Agent Skills Catalog (SKILL.md)
│   ├── agentic-harness-patterns/ # Comprehensive harness patterns & 12 reference guides
│   ├── memory-persistence/       # 3-tier memory management & 2-step save pattern
│   ├── context-engineering/      # Progressive disclosure & reactive compaction
│   └── tool-permission-guard/    # Fail-closed registry & permission pipelines
└── tests/                        # Comprehensive test suite
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

Clone and install in editable mode:

```bash
cd agentic-harness-skills
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Alternatively with standard `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## CLI Usage

The package includes a CLI utility `agentic-harness-skills` (or `python -m agentic_harness_skills`):

### 1. List Available Skills
Scans skill directories and displays metadata, token footprint, and trigger summaries:

```bash
agentic-harness-skills list
```

### 2. Validate Skill Formats & Token Budgets
Ensures that all `SKILL.md` definitions adhere to YAML frontmatter rules and strict token/character caps:

```bash
agentic-harness-skills validate
```

### 3. Inspect a Skill
Display the parsed metadata, triggers, and full markdown body of any skill:

```bash
agentic-harness-skills inspect memory-persistence
```

---

## Skill Format Standard (`SKILL.md`)

Each skill is encapsulated inside its own subdirectory within `skills/<skill-name>/SKILL.md`:

```markdown
---
name: memory-persistence
description: Manage persistent agent memory across sessions using a 2-step save invariant.
when_to_use: Triggers on: memory, persistent memory, session learning, cross-session recall.
license: MIT
version: 1.0.0
---

# Memory Persistence Skill

Instructions, workflows, and behavioral rules...
```

### Key Rules for Skill Authoring
1. **Front-Load Trigger Language**: Skill listing budgets are hard-capped. Ensure the most distinctive trigger words are at the beginning of `when_to_use` and `description`.
2. **Lazy Loading Invariant**: Do not place large reference datasets in `when_to_use`. Keep frontmatter metadata under 500 characters.
3. **Fail-Closed by Default**: When providing tool definitions within skills, always require explicit permission gating for side-effecting operations.

---

## Running Tests

Run the test suite using `pytest`:

```bash
uv run pytest -v
```

Lint and format checking:

```bash
uv run ruff check .
```

---

## Acknowledgments
- The pattern documentation in `skills/agentic-harness-patterns/` is based on the work by [Keli Wen](https://github.com/keli-wen/agentic-harness-patterns-skill).

## License

MIT License. See [LICENSE](LICENSE) for details.
