"""Tests for the Phase 4 two-layer weekly audit contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import weekly_result_check as check


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _base(command: str = "reconcile") -> dict:
    return {
        "schema_version": 1,
        "run_id": "run-1",
        "week": "2026-W32",
        "command": command,
        "completed": True,
        "status": "passed",
        "lint_report": "lint-2026-W32.json",
        "work_items": [{"id": "item-1", "source": "20_WIKI/demo.md"}],
        "processed": [{"id": "item-1", "path": "20_WIKI/demo.md"}],
        "skipped": [],
        "out_of_scope": [],
        "rewritten": [],
        "conflicts": [],
        "drafts": [],
        "log_rows": [],
        "errors": [],
    }


def _snapshots(tmp_path: Path):
    _write(tmp_path, "20_WIKI/demo.md", "---\ntype: concept\nstatus: stable\n---\n\n# Demo\n")
    before_path = tmp_path / "before.json"
    before = check.write_snapshot(tmp_path, before_path)
    after_path = tmp_path / "after.json"
    after = check.write_snapshot(tmp_path, after_path, previous=before)
    return before, after, before_path, after_path


def test_valid_result_passes_with_complete_coverage(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    errors = check.validate_result(_base(), "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert errors == []


def test_missing_coverage_fails(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    result = _base()
    result["processed"] = []
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("coverage" in error for error in errors)


def test_skip_requires_closed_code_and_opening_evidence(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    result = _base()
    result["processed"] = []
    result["skipped"] = [{"id": "item-1", "code": "because", "evidence": "missing.md", "note": "skip"}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("invalid code" in error for error in errors)
    assert any("does not open" in error for error in errors)


def test_skip_requires_note_and_nonempty_lint_evidence(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    result = _base()
    result["processed"] = []
    result["skipped"] = [{"id": "item-1", "code": "no-evidence", "evidence": "lint:", "note": ""}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("lint finding id" in error for error in errors)
    assert any("needs a note" in error for error in errors)


def test_out_of_scope_requires_reason(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    result = _base()
    result["processed"] = []
    result["out_of_scope"] = [{"id": "item-1", "reason": ""}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("needs a reason" in error for error in errors)


def test_raw_change_fails_even_if_result_claims_success(tmp_path: Path):
    before, _, _, _ = _snapshots(tmp_path)
    _write(tmp_path, "10_RAW/source.md", "changed\n")
    after_path = tmp_path / "after.json"
    after = check.write_snapshot(tmp_path, after_path, previous=before)
    errors = check.validate_result(_base(), "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("10_RAW changed" in error for error in errors)


def test_append_only_and_user_block_are_enforced(tmp_path: Path):
    _write(tmp_path, "20_WIKI/demo-LOG.md", "old\n")
    _write(tmp_path, "20_WIKI/demo-INDEX.md", "<!-- @user:start -->\nkeep\n<!-- @user:end -->\n")
    before_path = tmp_path / "before.json"
    before = check.write_snapshot(tmp_path, before_path)
    _write(tmp_path, "20_WIKI/demo-LOG.md", "new\n")
    _write(tmp_path, "20_WIKI/demo-INDEX.md", "<!-- @user:start -->\nlost\n<!-- @user:end -->\n")
    # Preserve the P-2 contract's metadata-first path while ensuring the
    # simulated write has a changed mtime on filesystems with coarse clocks.
    for relative in ("20_WIKI/demo-LOG.md", "20_WIKI/demo-INDEX.md"):
        path = tmp_path / relative
        old_mtime = before["entries"][relative]["mtime_ns"]
        path.touch()
        path_mtime = max(path.stat().st_mtime_ns, old_mtime + 1)
        import os

        os.utime(path, ns=(path_mtime, path_mtime))
    after_path = tmp_path / "after.json"
    after = check.write_snapshot(tmp_path, after_path, previous=before)
    result = _base()
    result["rewritten"] = [{"path": "20_WIKI/demo-LOG.md"}, {"path": "20_WIKI/demo-INDEX.md"}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert any("append-only" in error for error in errors)
    assert any("@user" in error for error in errors)


def test_append_only_allows_newest_first_top_insertion(tmp_path: Path):
    _write(tmp_path, "20_WIKI/demo-LOG.md", "# hub\n\n## 2026-08-26\n\n| a | b |\n")
    before_path = tmp_path / "before.json"
    before = check.write_snapshot(tmp_path, before_path)
    _write(tmp_path, "20_WIKI/demo-LOG.md", "# hub\n\n## 2026-09-07\n\n| c | d |\n\n## 2026-08-26\n\n| a | b |\n")
    for relative in ("20_WIKI/demo-LOG.md",):
        path = tmp_path / relative
        old_mtime = before["entries"][relative]["mtime_ns"]
        path.touch()
        path_mtime = max(path.stat().st_mtime_ns, old_mtime + 1)
        import os

        os.utime(path, ns=(path_mtime, path_mtime))
    after_path = tmp_path / "after.json"
    after = check.write_snapshot(tmp_path, after_path, previous=before)
    result = _base()
    result["rewritten"] = [{"path": "20_WIKI/demo-LOG.md"}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert not any("append-only" in error for error in errors)


def test_append_only_ignores_crlf_lf_normalization(tmp_path: Path):
    import os

    relative = "20_WIKI/demo-LOG.md"
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"# hub\r\n\r\n## 2026-08-26\r\n\r\n| a | b |\r\n")
    before_path = tmp_path / "before.json"
    before = check.write_snapshot(tmp_path, before_path)
    path.write_bytes(b"# hub\n\n## 2026-09-07\n\n| c | d |\n\n## 2026-08-26\n\n| a | b |\n")
    old_mtime = before["entries"][relative]["mtime_ns"]
    new_mtime = max(path.stat().st_mtime_ns, old_mtime + 1)
    os.utime(path, ns=(new_mtime, new_mtime))
    after_path = tmp_path / "after.json"
    after = check.write_snapshot(tmp_path, after_path, previous=before)
    result = _base()
    result["rewritten"] = [{"path": relative}]
    errors = check.validate_result(result, "reconcile", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert not any("append-only" in error for error in errors)


def test_synthesize_draft_contract(tmp_path: Path):
    before, after, _, _ = _snapshots(tmp_path)
    draft = _write(tmp_path, "20_WIKI/concepts/candidate.md", "---\ntype: concept\nstatus: draft\nauto_generated: true\nprojects:\n  - a\n  - b\n---\n\n# Candidate\n")
    result = _base("synthesize")
    result["work_items"] = [{"id": "candidate-1", "source": "20_WIKI/source.md"}]
    result["processed"] = [{"id": "candidate-1", "path": "20_WIKI/concepts/candidate.md"}]
    result["drafts"] = [{"path": "20_WIKI/concepts/candidate.md"}]
    errors = check.validate_result(result, "synthesize", "run-1", "2026-W32", Path("lint-2026-W32.json"), before, after, tmp_path)
    assert errors == []
    assert draft.exists()


def test_audit_requires_pass_and_matching_identity():
    valid = {"schema_version": 1, "run_id": "run-1", "week": "2026-W32", "verdict": "pass", "findings": []}
    assert check.validate_audit(valid, "run-1", "2026-W32") == []
    invalid = {**valid, "verdict": "fail"}
    assert check.validate_audit(invalid, "run-1", "2026-W32")
    finding_fail = {**valid, "findings": [{"check": "history", "severity": "high", "evidence": "20_WIKI/demo.md", "verdict": "fail"}]}
    assert check.validate_audit(finding_fail, "run-1", "2026-W32")
    finding_unknown = {**valid, "findings": [{"check": "history", "severity": "high", "evidence": "20_WIKI/demo.md", "verdict": "uncertain"}]}
    assert check.validate_audit(finding_unknown, "run-1", "2026-W32")


def test_duplicate_json_keys_are_rejected(tmp_path: Path):
    path = tmp_path / "result.json"
    path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(check.GateError, match="duplicate JSON key"):
        check.load_json(path)
