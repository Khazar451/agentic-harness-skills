"""Tests for SkillRunner execution modes and history tracking."""

from pathlib import Path

from agentic_harness_skills.core.runner import ExecutionMode, SkillRunner
from agentic_harness_skills.core.schema import parse_skill_markdown


def test_runner_inline_and_isolated(tmp_path: Path):
    content = """---
name: sample-runner-skill
description: Tests runner execution logic.
when_to_use: "Triggers on: runner test."
---

# Instructions
Execute task with given parameters.
"""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    skill_def = parse_skill_markdown(content, skill_file)

    runner = SkillRunner()

    # Test default inline execution
    res1 = runner.execute(skill_def, {"param": "val1"})
    assert res1.success is True
    assert res1.mode == ExecutionMode.INLINE
    assert res1.output["args"]["param"] == "val1"

    # Test isolated execution
    res2 = runner.execute(skill_def, {"param": "val2"}, mode=ExecutionMode.ISOLATED)
    assert res2.success is True
    assert res2.mode == ExecutionMode.ISOLATED

    # Test history
    assert len(runner.history) == 2
