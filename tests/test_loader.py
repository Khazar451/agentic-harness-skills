"""Tests for SkillCatalogLoader and two-phase discovery."""

from pathlib import Path

from agentic_harness_skills.core.loader import SkillCatalogLoader


def test_discover_skills_in_skills_dir():
    skills_dir = Path(__file__).parent.parent / "skills"
    loader = SkillCatalogLoader(search_paths=[skills_dir])

    discovered = loader.discover()
    assert "memory-persistence" in discovered
    assert "context-engineering" in discovered
    assert "tool-permission-guard" in discovered


def test_lazy_loading():
    skills_dir = Path(__file__).parent.parent / "skills"
    loader = SkillCatalogLoader(search_paths=[skills_dir])

    # Phase 1: Discovered, but full body not yet cached
    assert "memory-persistence" not in loader._loaded_cache
    loader.discover()
    assert "memory-persistence" not in loader._loaded_cache

    # Phase 2: Explicit load triggers body retrieval
    skill_def = loader.load_skill("memory-persistence")
    assert "memory-persistence" in loader._loaded_cache
    assert "Two-Step Save Invariant" in skill_def.body


def test_render_system_prompt_catalog():
    skills_dir = Path(__file__).parent.parent / "skills"
    loader = SkillCatalogLoader(search_paths=[skills_dir])

    rendered = loader.render_system_prompt_catalog()
    assert "<available_skills>" in rendered
    assert '<skill name="memory-persistence"' in rendered
    assert "</available_skills>" in rendered
