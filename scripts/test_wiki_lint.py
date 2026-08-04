"""Regression tests for the Phase 1 vault-lint classification rules."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import wiki_lint as lint


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _wiki_page(root: Path, relative: str, body: str = "# Note\n\ncontent\n") -> Path:
    return _write(root, f"20_WIKI/{relative}", f"---\ntype: note\n---\n\n{body}")


def _lint(root: Path) -> dict:
    return lint.lint_vault(root, as_of="2026-08-03")


def _paths(report: dict, key: str) -> set[str]:
    return {item["path"] for item in report[key] if "path" in item}


def test_raw_projects_are_not_structural_findings(tmp_path: Path):
    _wiki_page(tmp_path, "page.md")
    _write(tmp_path, "10_RAW/projects/demo/raw.md", "# Raw note\n")

    report = _lint(tmp_path)

    assert "10_RAW/projects/demo/raw.md" not in _paths(report, "missing_frontmatter")
    assert "10_RAW/projects/demo/raw.md" not in _paths(report, "orphans")
    assert "10_RAW/projects/demo/raw.md" not in _paths(report, "empty_sections")


def test_raw_outbound_links_are_only_raw_reference_notes(tmp_path: Path):
    _wiki_page(tmp_path, "page.md")
    _write(tmp_path, "10_RAW/projects/demo/raw.md", "[[missing-note]]\n")

    report = _lint(tmp_path)

    assert report["dead_links"] == []
    assert report["ambiguous_targets"] == []
    assert len(report["raw_reference_notes"]) == 1
    assert report["raw_reference_notes"][0]["source"] == "10_RAW/projects/demo/raw.md"


def test_index_links_do_not_rescue_an_orphan(tmp_path: Path):
    _wiki_page(tmp_path, "page.md")
    _write(tmp_path, "INDEX.md", "# Catalog\n\n[[20_WIKI/page]]\n")

    report = _lint(tmp_path)

    assert "20_WIKI/page.md" in _paths(report, "orphans")


def test_index_outbound_broken_links_are_still_scanned(tmp_path: Path):
    _wiki_page(tmp_path, "page.md")
    _write(tmp_path, "INDEX.md", "# Catalog\n\n[[20_WIKI/missing]]\n")

    report = _lint(tmp_path)

    assert any(item["source"] == "INDEX.md" for item in report["dead_links"])


def test_tier_two_index_and_log_pages_are_not_orphans(tmp_path: Path):
    _wiki_page(tmp_path, "projects/projects-INDEX.md")
    _wiki_page(tmp_path, "projects/projects-LOG.md")

    report = _lint(tmp_path)

    assert "20_WIKI/projects/projects-INDEX.md" not in _paths(report, "orphans")
    assert "20_WIKI/projects/projects-LOG.md" not in _paths(report, "orphans")


def test_catalog_stale_reports_pages_missing_from_generated_section(tmp_path: Path):
    _wiki_page(tmp_path, "a.md")
    _wiki_page(tmp_path, "b.md")
    _write(
        tmp_path,
        "INDEX.md",
        "# Catalog\n\n"
        "<!-- @generated:start -->\n"
        "- [[20_WIKI/a]]\n"
        "<!-- @generated:end -->\n",
    )

    report = _lint(tmp_path)

    assert report["catalog_stale"] == [{"path": "20_WIKI/b.md"}]


def test_project_synthesis_is_not_required_in_root_catalog(tmp_path: Path):
    _wiki_page(tmp_path, "projects/demo/demo.md")
    _wiki_page(tmp_path, "projects/demo/synthesis.md")
    _write(
        tmp_path,
        "INDEX.md",
        "<!-- @generated:start -->\n"
        "- [[20_WIKI/projects/demo/demo]]\n"
        "<!-- @generated:end -->\n",
    )

    report = _lint(tmp_path)

    assert report["catalog_stale"] == []


def test_path_qualified_link_resolves_despite_duplicate_basenames(tmp_path: Path):
    _wiki_page(tmp_path, "left/duplicate.md")
    _wiki_page(tmp_path, "right/duplicate.md")
    _wiki_page(tmp_path, "source.md", "[[20_WIKI/left/duplicate]]\n")

    report = _lint(tmp_path)

    assert not any(
        item["source"] == "20_WIKI/source.md" for item in report["ambiguous_targets"]
    )


def test_allowlisted_dangling_link_is_separated(tmp_path: Path):
    _wiki_page(tmp_path, "page.md", "[[10_RAW/assets/US-MSFT/]]\n")
    _write(
        tmp_path,
        ".vault-meta/lint-allowlist.json",
        '{"dangling_links": ["10_RAW/assets/US-MSFT/"]}\n',
    )

    report = _lint(tmp_path)

    assert report["dead_links"] == []
    assert len(report["allowlisted_dangling_links"]) == 1


def test_lint_is_read_only(tmp_path: Path):
    _wiki_page(tmp_path, "page.md", "[[missing-note]]\n")
    _write(tmp_path, "INDEX.md", "# Catalog\n")

    def snapshot() -> dict[str, tuple[str, int]]:
        result: dict[str, tuple[str, int]] = {}
        for path in sorted(tmp_path.rglob("*")):
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                result[path.relative_to(tmp_path).as_posix()] = (digest, path.stat().st_mtime_ns)
        return result

    before = snapshot()
    _lint(tmp_path)
    after = snapshot()

    assert after == before
