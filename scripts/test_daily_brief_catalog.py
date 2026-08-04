"""Phase 2 tests for the INDEX.md catalog generator and dry-run contract."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import daily_brief as db


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_catalog_preserves_user_block_and_lists_all_markdown_pages(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
    _write(
        tmp_path,
        "20_WIKI/projects/demo/demo.md",
        "---\ntype: project-index\n---\n\n# Demo\n\nActual project description.\n",
    )
    _write(
        tmp_path,
        "20_WIKI/projects/demo/stage-1.md",
        "---\ntype: project-stage\n---\n\n# Stage 1\n\nStage description.\n",
    )
    _write(tmp_path, "20_WIKI/projects/demo/synthesis.md", "---\ntype: project-synthesis\n---\n\n# Synthesis\n")
    _write(tmp_path, "20_WIKI/concepts/example.md", "---\ntype: concept\ndescription: Example concept\n---\n")
    existing = "# old\n\n<!-- @user:start -->\nKeep this note\n<!-- @user:end -->\n"

    content = db.build_catalog_index(existing)

    assert "Keep this note" in content
    assert "<!-- @generated:start -->" in content
    assert "<!-- @generated:end -->" in content
    assert "[[20_WIKI/projects/demo/demo|demo]]" in content
    assert "[[20_WIKI/projects/demo/synthesis|synthesis]]" not in content
    assert "  - [[20_WIKI/projects/demo/stage-1|stage-1]]" in content
    assert "Example concept" in content
    assert "Actual project description." in content


def test_table_wikilink_escapes_alias_pipe():
    assert db._wikilink("20_WIKI/entities/duckdb", "duckdb", table=True) == (
        r"[[20_WIKI/entities/duckdb\|duckdb]]"
    )


def test_catalog_creates_empty_user_block_when_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
    _write(tmp_path, "20_WIKI/concepts/example.md", "---\ntype: concept\n---\n")

    content = db.build_catalog_index("")

    assert content.count("<!-- @user:start -->") == 1
    assert content.count("<!-- @user:end -->") == 1


def test_catalog_counts_markdown_only(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
    _write(tmp_path, "20_WIKI/concepts/example.md", "---\ntype: concept\n---\n")
    _write(tmp_path, "20_WIKI/concepts/.gitkeep", "")

    content = db.build_catalog_index("")

    assert "> 20_WIKI Markdown pages: 1 " in content
    assert ".gitkeep" not in content
