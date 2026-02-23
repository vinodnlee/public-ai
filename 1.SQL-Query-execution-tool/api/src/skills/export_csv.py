"""
Built-in skill: export query result as CSV string.
"""

import csv
import io
import json
from typing import Any

from langchain_core.tools import tool

from src.skills.registry import Skill, SkillTarget, register_skill


def export_result_csv_tool(columns: list[str], rows: list[dict[str, Any]]) -> str:
    """Format columns and rows as a CSV string. Header is the first line."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row.get(c) for c in columns])
    return buf.getvalue()


@tool
def export_result_as_csv(columns_json: str, rows_json: str) -> str:
    """Export a query result as CSV text.

    Args:
        columns_json: JSON array of column names, e.g. ["name", "count"].
        rows_json: JSON array of row objects, e.g. [{"name":"a","count":1}].

    Returns:
        CSV string with header row and data rows.
    """
    columns = json.loads(columns_json)
    rows = json.loads(rows_json)
    return export_result_csv_tool(columns=columns, rows=rows)


def register_export_csv_skill() -> None:
    """Register the export_csv built-in skill."""
    register_skill(Skill(
        id="export_csv",
        name="Export result as CSV",
        description="Export the last query result as CSV text.",
        tools=[export_result_as_csv],
        target=SkillTarget.SUPERVISOR,
    ))
