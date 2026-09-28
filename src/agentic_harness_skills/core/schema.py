"""Schema and validation models for Agentic Harness Skills."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class SkillMetadata(BaseModel):
    """Metadata extracted from the skill's YAML frontmatter.

    Designed following the Agentic Harness Patterns:
    - Discovery must be cheap (compact representation).
    - Front-loaded trigger phrasing.
    - Strict character limits to fit within budget limits.
    """

    name: str = Field(..., description="Unique kebab-case name of the skill")
    description: str = Field(..., description="High-level description of what the skill does")
    when_to_use: Optional[str] = Field(
        default=None,
        description="Conditions and trigger phrases for when the skill should activate",
    )
    license: Optional[str] = Field(default="MIT", description="Software license")
    version: Optional[str] = Field(default="1.0.0", description="Semantic version of the skill")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(
                f"Skill name '{v}' must be lowercase kebab-case (e.g., 'memory-persistence')"
            )
        return v

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: str) -> str:
        cleaned = " ".join(v.strip().split())
        if len(cleaned) > 500:
            raise ValueError(
                f"Skill description exceeds 500 characters limit ({len(cleaned)} chars). "
                "Keep descriptions compact for cheap discovery."
            )
        return cleaned

    def compact_summary(self, max_chars: int = 150) -> str:
        """Returns a compact summary string suitable for catalog prompt injection."""
        trigger = f" [Triggers: {self.when_to_use}]" if self.when_to_use else ""
        combined = f"{self.name}: {self.description}{trigger}"
        if len(combined) > max_chars:
            return combined[: max_chars - 3] + "..."
        return combined

    def estimated_prompt_tokens(self) -> int:
        """Rough estimate of token consumption when injected into system prompts."""
        return max(1, len(self.compact_summary()) // 4)


class SkillDefinition(BaseModel):
    """Full skill representation including body instructions and location."""

    metadata: SkillMetadata
    body: str = Field(..., description="Full Markdown instructional body of the skill")
    path: Path = Field(..., description="Filesystem path to the SKILL.md file")

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def total_estimated_tokens(self) -> int:
        """Total estimated tokens for full activation (frontmatter + body)."""
        return max(1, (len(self.metadata.model_dump_json()) + len(self.body)) // 4)


def parse_skill_markdown(content: str, path: Path) -> SkillDefinition:
    """Parses a markdown string containing YAML frontmatter into a SkillDefinition."""
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"File at '{path}' is missing YAML frontmatter enclosed in '---' markers.")

    raw_yaml, body = frontmatter_match.groups()
    try:
        data: dict[str, Any] = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in frontmatter at '{path}': {exc}") from exc

    metadata = SkillMetadata(**data)
    return SkillDefinition(metadata=metadata, body=body.strip(), path=path)
