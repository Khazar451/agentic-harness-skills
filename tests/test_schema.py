"""Tests for SkillMetadata, SkillDefinition, and frontmatter parsing."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from agentic_harness_skills.core.schema import (
    SkillMetadata,
    parse_skill_markdown,
)


def test_valid_skill_metadata():
    meta = SkillMetadata(
        name="test-skill",
        description="A test skill for verifying schema parsing.",
        when_to_use="Triggers on: test, verification.",
    )
    assert meta.name == "test-skill"
    assert meta.version == "1.0.0"
    assert meta.license == "MIT"
    assert "test-skill" in meta.compact_summary()
    assert meta.estimated_prompt_tokens() > 0


def test_invalid_skill_name():
    with pytest.raises(ValidationError):
        SkillMetadata(
            name="Invalid_Skill_Name",
            description="Should fail due to uppercase and underscores.",
        )


def test_description_length_cap():
    too_long_desc = "x" * 501
    with pytest.raises(ValidationError):
        SkillMetadata(
            name="oversized-skill",
            description=too_long_desc,
        )


def test_parse_skill_markdown(tmp_path: Path):
    skill_file = tmp_path / "SKILL.md"
    content = """---
name: custom-workflow
description: Custom test workflow instructions.
when_to_use: "Triggers on: custom workflow."
version: 2.1.0
---

# Custom Instructions
Step 1: Do this.
Step 2: Do that.
"""
    skill_file.write_text(content, encoding="utf-8")
    definition = parse_skill_markdown(content, skill_file)

    assert definition.name == "custom-workflow"
    assert definition.metadata.version == "2.1.0"
    assert "Step 1: Do this." in definition.body
    assert definition.total_estimated_tokens > 0


def test_parse_missing_frontmatter(tmp_path: Path):
    invalid_file = tmp_path / "SKILL.md"
    invalid_file.write_text("# Just Markdown, No Frontmatter", encoding="utf-8")

    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        parse_skill_markdown(invalid_file.read_text(), invalid_file)
