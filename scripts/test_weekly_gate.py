"""Tests for the weekly pipeline marker and lint gate."""

from __future__ import annotations

import sys
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import weekly_gate as gate


def lint_result(tmp_path: Path, *, rc: int = 0, text: str = "lint report\n"):
    markdown = tmp_path / "lint.md"
    lint_json = tmp_path / "lint.json"
    markdown.write_text(text, encoding="utf-8")
    lint_json.write_text('{"findings": []}\n', encoding="utf-8")
    return rc, markdown, lint_json, text


def test_iso_week_is_stable():
    from datetime import datetime

    assert gate.iso_week(datetime(2026, 8, 3)) == "2026-W32"


def test_same_week_skips_before_lint(tmp_path: Path, monkeypatch, capsys):
    marker = tmp_path / ".weekly_last_run"
    marker.write_text("2026-W32", encoding="utf-8")
    monkeypatch.setattr(gate, "MARKER_PATH", marker)
    monkeypatch.setattr(gate, "iso_week", lambda: "2026-W32")
    monkeypatch.setattr(gate, "_lint_report", lambda _: pytest.fail("lint must not run"))

    assert gate.run() == 0
    assert "already completed" in capsys.readouterr().out


def test_dry_run_does_not_write_marker(tmp_path: Path, monkeypatch, capsys):
    marker = tmp_path / ".weekly_last_run"
    monkeypatch.setattr(gate, "MARKER_PATH", marker)
    monkeypatch.setattr(gate, "_lint_report", lambda week: lint_result(tmp_path))
    monkeypatch.setattr(gate, "iso_week", lambda: "2026-W32")

    assert gate.run(dry_run=True) == 0
    assert not marker.exists()
    assert "reconcile -> Python check -> synthesize" in capsys.readouterr().out


def test_lint_dead_or_ambiguous_links_block_writer(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(gate, "STATE_DIR", tmp_path)

    def fake_run(args, **kwargs):
        if "markdown" in args:
            return SimpleNamespace(returncode=0, stdout="lint report\n", stderr="")
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"dead_links": [{"source": "20_WIKI/a.md"}], "ambiguous_targets": []}),
            stderr="",
        )

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    rc, _, _, _ = gate._lint_report("2026-W32")
    assert rc == 1


def test_auditor_parser_accepts_strict_json_code_fence():
    payload = {"schema_version": 1, "run_id": "r", "week": "2026-W32", "verdict": "pass", "findings": []}
    parsed = gate._parse_auditor_stdout("```json\n" + json.dumps(payload) + "\n```")
    assert parsed == payload


def test_success_writes_marker_after_claude(tmp_path: Path, monkeypatch):
    marker = tmp_path / ".weekly_last_run"
    calls = []
    state = {
        "schema_version": 1,
        "run_id": "test-run",
        "week": "2026-W32",
        "status": "running",
        "reconcile": "pending",
        "synthesize": "pending",
        "finalize": "pending",
        "audit": "pending",
    }
    monkeypatch.setattr(gate, "MARKER_PATH", marker)
    monkeypatch.setattr(gate, "STATE_DIR", tmp_path)
    monkeypatch.setattr(gate, "RESULT_DIR", tmp_path / "weekly")
    monkeypatch.setattr(gate, "_lint_report", lambda week: lint_result(tmp_path))
    monkeypatch.setattr(gate, "iso_week", lambda: "2026-W32")
    monkeypatch.setattr(gate, "_load_or_start", lambda week, report_only: state)
    monkeypatch.setattr(gate, "_save_state", lambda week, current: None)
    monkeypatch.setattr(gate, "_run_writer", lambda command, prompt: calls.append(command) or 0)
    monkeypatch.setattr(
        gate,
        "_snapshot_pair",
        lambda label, week, previous=None: ({"entries": {}}, tmp_path / f"{label}.json"),
    )
    monkeypatch.setattr(gate, "_validate_stage", lambda *args: calls.append("check") or 0)
    monkeypatch.setattr(gate, "_run_auditor", lambda *args: calls.append("audit") or 0)
    monkeypatch.setattr(gate.checker, "load_json", lambda path: {"entries": {}})

    assert gate.run() == 0
    assert marker.read_text(encoding="utf-8") == "2026-W32"
    assert calls == ["reconcile", "check", "synthesize", "check", "finalize", "audit"]


def test_lint_failure_does_not_call_claude_or_write_marker(tmp_path: Path, monkeypatch):
    marker = tmp_path / ".weekly_last_run"
    monkeypatch.setattr(gate, "MARKER_PATH", marker)
    monkeypatch.setattr(gate, "_lint_report", lambda week: lint_result(tmp_path, rc=1, text="lint failed\n"))
    monkeypatch.setattr(gate, "_run_writer", lambda *args: pytest.fail("Claude must not run"))

    assert gate.run() == 1
    assert not marker.exists()
