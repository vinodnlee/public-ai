"""
Tests for skill_loader: scan dirs for **/SKILL.md, parse to (path, title, content).
"""

import pytest

from src.skills.skill_loader import load_skills_from_dirs, SkillDoc


def test_load_skills_from_dirs_empty_dirs_returns_empty_list() -> None:
    """When skill_dirs is empty, return empty list."""
    assert load_skills_from_dirs([]) == []


def test_load_skills_from_dirs_nonexistent_dir_returns_empty_list() -> None:
    """When a dir does not exist, skip it and return empty (or only from existing dirs)."""
    result = load_skills_from_dirs(["/nonexistent/path/12345"])
    assert result == []


def test_load_skills_from_dirs_finds_skill_md_and_parses_title_and_content(
    tmp_path: pytest.TempPathFactory,
) -> None:
    """Scan a dir with SKILL.md; return SkillDoc with path, title from first # line, content."""
    (tmp_path / "my-skill").mkdir()
    skill_file = tmp_path / "my-skill" / "SKILL.md"
    skill_file.write_text("# My Skill Title\n\nThis is the skill content.\n", encoding="utf-8")

    result = load_skills_from_dirs([str(tmp_path)])

    assert len(result) == 1
    assert isinstance(result[0], SkillDoc)
    assert result[0].path == str(skill_file)
    assert result[0].title == "My Skill Title"
    assert "This is the skill content" in result[0].content
    assert "My Skill Title" in result[0].content


def test_load_skills_from_dirs_multiple_files_and_dirs(tmp_path: pytest.TempPathFactory) -> None:
    """Multiple dirs and nested SKILL.md files are all returned."""
    (tmp_path / "a").mkdir()
    (tmp_path / "b" / "nested").mkdir(parents=True)
    (tmp_path / "a" / "SKILL.md").write_text("# Skill A\n\nContent A.", encoding="utf-8")
    (tmp_path / "b" / "nested" / "SKILL.md").write_text("# Skill B\n\nContent B.", encoding="utf-8")

    result = load_skills_from_dirs([str(tmp_path)])

    assert len(result) == 2
    titles = {r.title for r in result}
    assert titles == {"Skill A", "Skill B"}
    paths = {r.path for r in result}
    assert any("a" in p and "SKILL.md" in p for p in paths)
    assert any("nested" in p and "SKILL.md" in p for p in paths)


def test_load_skills_from_dirs_no_heading_uses_filename_or_dir(tmp_path: pytest.TempPathFactory) -> None:
    """When SKILL.md has no # heading, title falls back to parent dir name or 'SKILL.md'."""
    (tmp_path / "no-heading").mkdir()
    (tmp_path / "no-heading" / "SKILL.md").write_text("Just content, no heading.\n", encoding="utf-8")

    result = load_skills_from_dirs([str(tmp_path)])

    assert len(result) == 1
    assert result[0].title  # non-empty
    assert "Just content" in result[0].content
