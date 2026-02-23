"""
Load SKILL.md files from configured directories for prompt injection and discovery.

Scans each directory for **/SKILL.md, reads content, and extracts a title from the first # heading
or falls back to the parent directory name.
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillDoc:
    """A loaded SKILL.md: file path, title (from first # or fallback), and full content."""

    path: str
    title: str
    content: str


def _title_from_content(content: str, fallback_path: str) -> str:
    """Extract title from first # heading, or use fallback (e.g. parent dir name)."""
    first_line = content.split("\n")[0].strip()
    match = re.match(r"^#\s+(.+)$", first_line)
    if match:
        return match.group(1).strip()
    try:
        return Path(fallback_path).parent.name
    except Exception:
        return "SKILL.md"


def load_skills_from_dirs(dirs: list[str]) -> list[SkillDoc]:
    """
    Scan each directory for **/SKILL.md; read and parse each into SkillDoc (path, title, content).

    Non-existent or non-directory entries are skipped. Encoding is UTF-8.
    """
    result: list[SkillDoc] = []
    for d in dirs:
        path = Path(d)
        if not path.is_dir():
            continue
        for skill_path in path.rglob("SKILL.md"):
            if not skill_path.is_file():
                continue
            try:
                content = skill_path.read_text(encoding="utf-8")
            except Exception:
                continue
            title = _title_from_content(content, str(skill_path))
            result.append(
                SkillDoc(path=str(skill_path), title=title, content=content.strip())
            )
    return result
