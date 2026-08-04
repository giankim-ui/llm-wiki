"""Phase 3 tests for Stage routing, manifest safety, and graph validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import stage_ingest_gate as gate


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _modes(path: Path, projects: dict[str, str] | None = None) -> None:
    path.write_text(json.dumps({"schema_version": 1, "projects": projects or {"demo": "stage"}, "default_mode": "legacy"}), encoding="utf-8")


def _stage(number: int, slug: str, status: str, prev: str | None, next_stage: str | None, link: str = "source") -> str:
    def link_or_empty(value: str | None) -> str:
        return f'"[[{value}]]"' if value else "null"

    return f'''---
type: project-stage
project: {slug}
stage: {number}
stage_slug: stage-{number}
status: {status}
parent: "[[{slug}]]"
prev: {link_or_empty(prev)}
next: {link_or_empty(next_stage)}
---

# Stage {number}

## 흐름

| # | 파일 |
|---|---|
| 1 | [[{link}]] |
'''


def _graph(root: Path, active: int = 1) -> None:
    _write(root, "20_WIKI/projects/demo/demo.md", f'''---
type: project-index
stage_enabled: true
current_stage: {active}
current_phase: stage-{active}
---

# Demo

## Stage Map

- [[stage-0-seed]]
- [[stage-1-build]]
''')
    _write(root, "20_WIKI/projects/demo/stage-0-seed.md", _stage(0, "demo", "active" if active == 0 else "done", None, "stage-1-build"))
    _write(root, "20_WIKI/projects/demo/stage-1-build.md", _stage(1, "demo", "active" if active == 1 else "done", "stage-0-seed", None))
    _write(root, "20_WIKI/projects/demo/synthesis.md", "---\ntype: project-synthesis\n---\n\n# Synthesis\n\n[[source]]\n")


def test_valid_graph_passes(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes)
    _graph(tmp_path)
    assert gate.validate_graph(tmp_path, modes) == []


def test_graph_detects_broken_links_and_active_count(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes)
    _graph(tmp_path)
    stage = tmp_path / "20_WIKI/projects/demo/stage-1-build.md"
    stage.write_text(stage.read_text(encoding="utf-8").replace('status: active', 'status: done').replace('next: null', 'next: "[[missing]]"'), encoding="utf-8")
    errors = gate.validate_graph(tmp_path, modes)
    assert any("exactly one active" in error for error in errors)
    assert any("final Stage must not have next" in error for error in errors)


def test_stage_mode_without_bootstrap_is_safe_stop(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes, {"demo": "stage", "okr-matrix": "stage"})
    _write(tmp_path, "20_WIKI/projects/okr-matrix/okr-matrix.md", "---\ntype: project-index\nstage_enabled: true\ncurrent_stage: 0\ncurrent_phase: stage-0\n---\n")
    errors = gate.validate_graph(tmp_path, modes, "okr-matrix")
    assert any("STAGE_NOT_BOOTSTRAPPED" in error for error in errors)


def test_synthesis_assignment_gap_is_detected(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes)
    _graph(tmp_path)
    _write(tmp_path, "20_WIKI/projects/demo/synthesis.md", "---\ntype: project-synthesis\n---\n\n[[unassigned]]\n")
    errors = gate.validate_graph(tmp_path, modes)
    assert any("synthesis links not assigned" in error for error in errors)


def test_summary_prefers_title_then_h1_then_summary(tmp_path: Path):
    path = _write(tmp_path, "10_RAW/projects/demo/plans/v1.0.md", "---\ntitle: Front title\n---\n\n# H1\n\n## Summary\n\nUseful summary line.\n")
    assert gate._summary_for(path) == ("Front title", "Useful summary line.")
    path.write_text("# H1\n\n## 개요\n\n개요 문장\n", encoding="utf-8")
    assert gate._summary_for(path) == ("H1", "개요 문장")


def test_v1_0_wikilink_is_not_treated_as_extension():
    assert gate._link_target("plan-retention-app-260721-v1.0") == "plan-retention-app-260721-v1.0"


def test_manifest_filters_legacy_missing_and_consumed(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes, {"demo": "stage", "legacy": "legacy"})
    destination = _write(tmp_path, "10_RAW/projects/demo/plans/new.md", "# New\n\nSummary\n")
    manifest = {"schema_version": 1, "run_id": "r1", "completed": True, "consumed_at": None, "entries": [
        {"source": "old", "destination": str(destination), "slug": "demo", "type": "plans"},
        {"source": "old2", "destination": str(tmp_path / "10_RAW/projects/legacy/plans/x.md"), "slug": "legacy", "type": "plans"},
        {"source": "old3", "destination": str(tmp_path / "10_RAW/projects/new/plans/x.md"), "slug": "new", "type": "plans"},
    ]}
    manifest_path = tmp_path / "moved.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    loaded = gate.load_manifest(manifest_path)
    entries, warnings = gate._manifest_entries(loaded, gate.load_modes(modes), tmp_path)
    assert [entry["slug"] for entry in entries] == ["demo"]
    assert any("unregistered project" in warning for warning in warnings)

    loaded["entries"].append({"source": "old4", "destination": str(tmp_path / "10_RAW/projects/demo/plans/missing.md"), "slug": "demo", "type": "plans"})
    entries, warnings = gate._manifest_entries(loaded, gate.load_modes(modes), tmp_path)
    assert [entry["slug"] for entry in entries] == ["demo"]
    assert any("destination missing" in warning for warning in warnings)


def test_manifest_duplicate_is_rejected(tmp_path: Path):
    path = tmp_path / "moved.json"
    path.write_text(json.dumps({"schema_version": 1, "run_id": "r", "completed": True, "consumed_at": None, "entries": [
        {"source": "same", "destination": "a", "slug": "demo", "type": "plans"},
        {"source": "same", "destination": "b", "slug": "demo", "type": "plans"},
    ]}), encoding="utf-8")
    with pytest.raises(gate.GateError, match="duplicate"):
        gate.load_manifest(path)


def test_invalid_modes_duplicate_or_bad_value_stop(tmp_path: Path):
    path = tmp_path / "modes.json"
    path.write_text('{"schema_version":1,"projects":{"demo":"broken"},"default_mode":"legacy"}', encoding="utf-8")
    with pytest.raises(gate.GateError, match="invalid mode"):
        gate.load_modes(path)
    path.write_text('{"schema_version":1,"projects":{"demo":"stage","demo":"legacy"},"default_mode":"legacy"}', encoding="utf-8")
    with pytest.raises(gate.GateError, match="duplicate JSON key"):
        gate.load_modes(path)


def test_incomplete_manifest_produces_no_entries(tmp_path: Path):
    modes = tmp_path / "modes.json"
    _modes(modes)
    manifest = {"schema_version": 1, "run_id": "r", "completed": False, "consumed_at": None, "entries": []}
    assert gate._manifest_entries(manifest, gate.load_modes(modes), tmp_path) == ([], [])


def test_consume_marks_only_manifest(tmp_path: Path):
    manifest_path = tmp_path / "moved.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "run_id": "r1", "completed": True, "consumed_at": None, "entries": []}), encoding="utf-8")
    assert gate.consume_manifest(manifest_path, "r1") == 0
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["consumed_at"]
