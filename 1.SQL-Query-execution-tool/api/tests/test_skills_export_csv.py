"""
Tests for built-in skill: export_result_csv.
"""

import io
import csv

import pytest

from src.skills.export_csv import export_result_csv_tool


def test_export_result_csv_returns_csv_string_with_header_and_rows() -> None:
    """Tool should return a CSV string with header row and data rows."""
    columns = ["name", "count"]
    rows = [{"name": "a", "count": 1}, {"name": "b", "count": 2}]
    result = export_result_csv_tool(columns=columns, rows=rows)
    assert "name" in result and "count" in result
    assert "a,1" in result or "a," in result
    assert "b,2" in result or "b," in result
    # Parse as CSV to ensure valid
    reader = csv.reader(io.StringIO(result))
    lines = list(reader)
    assert len(lines) >= 2
    assert lines[0] == ["name", "count"]


def test_export_result_csv_escapes_commas_in_values() -> None:
    """Values containing commas should be quoted in CSV output."""
    columns = ["col"]
    rows = [{"col": "a,b"}]
    result = export_result_csv_tool(columns=columns, rows=rows)
    assert "a,b" in result
    reader = csv.reader(io.StringIO(result))
    lines = list(reader)
    assert len(lines) == 2
    assert lines[1] == ["a,b"]


def test_export_result_csv_empty_rows_returns_header_only() -> None:
    """Empty rows should still produce a header line."""
    columns = ["x"]
    rows: list[dict] = []
    result = export_result_csv_tool(columns=columns, rows=rows)
    reader = csv.reader(io.StringIO(result))
    lines = list(reader)
    assert len(lines) == 1
    assert lines[0] == ["x"]
