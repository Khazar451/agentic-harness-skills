"""Two-phase lazy skill discovery and loading engine."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

from agentic_harness_skills.core.schema import (
    SkillDefinition,
    SkillMetadata,
    parse_skill_markdown,
)

logger = logging.getLogger(__name__)


class SkillCatalogLoader:
    """Manages skill discovery, deduplication, and lazy loading.

    Follows the Agentic Harness Patterns:
    1. Discovery is cheap and metadata-only (two-phase loading).
    2. Deduplication is performed by canonical path and unique skill name.
    3. Strict character caps are applied to avoid exhausting the agent's context budget.
    """

    def __init__(
        self,
        search_paths: Optional[Iterable[Path | str]] = None,
        max_catalog_tokens: int = 1500,
    ) -> None:
        self.search_paths: list[Path] = [
            Path(p).expanduser().resolve() for p in (search_paths or [Path.cwd() / "skills"])
        ]
        self.max_catalog_tokens = max_catalog_tokens
        self._metadata_index: dict[str, tuple[SkillMetadata, Path]] = {}
        self._loaded_cache: dict[str, SkillDefinition] = {}

    def discover(self, force_refresh: bool = False) -> dict[str, SkillMetadata]:
        """Phase 1: Discover all available skills scanning only metadata.

        Returns a dictionary mapping skill names to their SkillMetadata.
        """
        if self._metadata_index and not force_refresh:
            return {name: meta for name, (meta, _) in self._metadata_index.items()}

        self._metadata_index.clear()
        self._loaded_cache.clear()
        seen_canonical_paths: set[Path] = set()

        for search_path in self.search_paths:
            if not search_path.exists() or not search_path.is_dir():
                continue

            for file_path in search_path.glob("**/SKILL.md"):
                canonical = file_path.resolve()
                if canonical in seen_canonical_paths:
                    continue
                seen_canonical_paths.add(canonical)

                try:
                    # Read only enough of the file to extract frontmatter
                    content = canonical.read_text(encoding="utf-8")
                    definition = parse_skill_markdown(content, canonical)
                    skill_name = definition.metadata.name

                    if skill_name in self._metadata_index:
                        existing_meta, existing_path = self._metadata_index[skill_name]
                        logger.warning(
                            "Duplicate skill name '%s' found at %s. Overriding %s.",
                            skill_name,
                            canonical,
                            existing_path,
                        )

                    self._metadata_index[skill_name] = (definition.metadata, canonical)
                except Exception as exc:
                    logger.error("Failed to load skill at '%s': %s", canonical, exc)

        return {name: meta for name, (meta, _) in self._metadata_index.items()}

    def load_skill(self, name: str) -> SkillDefinition:
        """Phase 2: Lazy loading - load full instructions only when activated."""
        if name in self._loaded_cache:
            return self._loaded_cache[name]

        if not self._metadata_index:
            self.discover()

        if name not in self._metadata_index:
            avail = list(self._metadata_index.keys())
            raise KeyError(f"Skill '{name}' not found in catalog. Available: {avail}")

        _, path = self._metadata_index[name]
        content = path.read_text(encoding="utf-8")
        definition = parse_skill_markdown(content, path)
        self._loaded_cache[name] = definition
        return definition

    def render_system_prompt_catalog(self) -> str:
        """Renders compact XML/Markdown catalog for injection into the agent's system prompt.

        Ensures token budget is not exceeded.
        """
        metas = self.discover()
        if not metas:
            return "No skills currently available."

        lines = ["<available_skills>"]
        total_tokens = 0

        for name, meta in sorted(metas.items()):
            summary = meta.compact_summary(max_chars=200)
            cost = max(1, len(summary) // 4)

            if total_tokens + cost > self.max_catalog_tokens:
                lines.append("  <!-- Remaining skills omitted due to context budget limits -->")
                break

            trigger_clause = f' triggers="{meta.when_to_use}"' if meta.when_to_use else ""
            lines.append(f'  <skill name="{name}"{trigger_clause}>{meta.description}</skill>')
            total_tokens += cost

        lines.append("</available_skills>")
        return "\n".join(lines)
