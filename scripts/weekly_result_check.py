"""Machine-check the two-layer weekly reconcile/synthesize audit contract.

The writer sessions produce result JSON, but JSON claims are never trusted by
themselves. This module compares pre/post snapshots, checks coverage and write
disclosures, enforces append-only and history rules, and validates the separate
read-only auditor result. Exit codes are 0=pass, 1=validation failure,
2=configuration or malformed-input error.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


VAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = VAULT_ROOT / ".vault-meta" / "weekly"
SNAPSHOT_EXTENSIONS = {".md", ".json", ".csv"}
SNAPSHOT_ROOTS = ("10_RAW", "20_WIKI")
EXCLUDED_PARTS = {"_attachments", "90_ARCHIVE", "archive", ".obsidian"}
SKIP_CODES = {"no-evidence", "authority-tie", "outside-scope", "weekly-cap", "privacy-boundary"}
ALLOWED_RESULT_STATUS = {"passed", "report-only"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


class GateError(ValueError):
    """Malformed contract or impossible gate configuration."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GateError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except FileNotFoundError as exc:
        raise GateError(f"result or snapshot file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"malformed JSON {path}: line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tracked_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative_root in SNAPSHOT_ROOTS:
        base = root / relative_root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SNAPSHOT_EXTENSIONS:
                continue
            relative = path.relative_to(root)
            if any(part in EXCLUDED_PARTS for part in relative.parts):
                continue
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def _user_block(raw: bytes) -> bytes | None:
    start = b"<!-- @user:start -->"
    end = b"<!-- @user:end -->"
    start_at = raw.find(start)
    end_at = raw.find(end)
    if start_at < 0 or end_at < start_at:
        return None
    end_at += len(end)
    return raw[start_at:end_at]


def _append_only(path: str) -> bool:
    name = Path(path).name
    return name == "synthesis.md" or name == "LOG.md" or name.endswith("-LOG.md")


def _index_file(path: str) -> bool:
    name = Path(path).name
    return name == "INDEX.md" or name.endswith("-INDEX.md") or name == "index.md"


def write_snapshot(root: Path, path: Path, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}
    previous_entries = previous.get("entries", {}) if previous else {}
    append_prefixes: dict[str, str] = {}
    user_blocks: dict[str, str] = {}
    for file_path in _tracked_files(root):
        relative = file_path.relative_to(root).as_posix()
        metadata = file_path.stat()
        current_meta = {"size": metadata.st_size, "mtime_ns": metadata.st_mtime_ns}
        previous_meta = previous_entries.get(relative, {}) if isinstance(previous_entries, dict) else {}
        if previous_meta.get("size") == metadata.st_size and previous_meta.get("mtime_ns") == metadata.st_mtime_ns and previous_meta.get("sha256"):
            current_meta["sha256"] = previous_meta["sha256"]
        else:
            current_meta["sha256"] = _sha256(file_path)
        entries[relative] = current_meta
        raw = file_path.read_bytes()
        if _append_only(relative):
            append_prefixes[relative] = base64.b64encode(raw).decode("ascii")
        if _index_file(relative):
            block = _user_block(raw)
            if block is not None:
                user_blocks[relative] = hashlib.sha256(block).hexdigest()
    snapshot = {
        "schema_version": 1,
        "entries": entries,
        "append_prefixes": append_prefixes,
        "user_blocks": user_blocks,
    }
    _atomic_write(path, snapshot)
    return snapshot


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def snapshot_diff(before: dict[str, Any], after: dict[str, Any], root: Path) -> dict[str, Any]:
    before_entries = before.get("entries", {})
    after_entries = after.get("entries", {})
    if not isinstance(before_entries, dict) or not isinstance(after_entries, dict):
        raise GateError("snapshot entries must be objects")
    all_paths = sorted(set(before_entries) | set(after_entries))
    changed: list[str] = []
    for relative in all_paths:
        old = before_entries.get(relative)
        new = after_entries.get(relative)
        if old is None or new is None or old.get("sha256") != new.get("sha256"):
            changed.append(relative)
    raw_changed = [path for path in changed if path.startswith("10_RAW/")]
    wiki_changed = [path for path in changed if path.startswith("20_WIKI/")]
    return {
        "changed": changed,
        "raw_changed": raw_changed,
        "wiki_changed": wiki_changed,
        "raw_unchanged": not raw_changed,
    }


def _require(data: dict[str, Any], keys: Iterable[str], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise GateError(f"{context} missing fields: {', '.join(missing)}")


def _list_field(data: dict[str, Any], key: str, context: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise GateError(f"{context}.{key} must be an array")
    return value


def _path_from_value(value: Any) -> str | None:
    if isinstance(value, str):
        return value.replace("\\", "/")
    if isinstance(value, dict):
        for key in ("path", "file", "target"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate.replace("\\", "/")
    return None


def _result_paths(data: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for key in ("processed", "rewritten", "conflicts", "drafts", "log_rows"):
        for value in data.get(key, []):
            path = _path_from_value(value)
            if path:
                paths.add(path)
    return paths


def _validate_common(data: dict[str, Any], command: str, run_id: str, week: str, lint_report: Path) -> list[str]:
    errors: list[str] = []
    _require(
        data,
        ("schema_version", "run_id", "week", "command", "completed", "status", "lint_report", "work_items", "processed", "skipped", "out_of_scope", "rewritten", "conflicts", "drafts", "log_rows", "errors"),
        command,
    )
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("run_id") != run_id:
        errors.append("run_id mismatch")
    if data.get("week") != week:
        errors.append("week mismatch")
    if data.get("command") != command:
        errors.append("command mismatch")
    if data.get("completed") is not True:
        errors.append("completed must be true")
    if data.get("status") not in ALLOWED_RESULT_STATUS:
        errors.append("status must be passed or report-only")
    if Path(str(data.get("lint_report"))).name != lint_report.name:
        errors.append("lint_report does not identify this run's report")
    for key in ("work_items", "processed", "skipped", "out_of_scope", "rewritten", "conflicts", "drafts", "log_rows", "errors"):
        try:
            _list_field(data, key, command)
        except GateError as exc:
            errors.append(str(exc))
    return errors


def _validate_coverage(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    work_items = _list_field(data, "work_items", data["command"])
    work_ids: list[str] = []
    for item in work_items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            errors.append("every work_item needs a non-empty id")
        else:
            work_ids.append(item["id"])
    if len(set(work_ids)) != len(work_ids):
        errors.append("duplicate work_item id")
    accounted: list[str] = []
    for key in ("processed", "skipped", "out_of_scope"):
        for item in _list_field(data, key, data["command"]):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                errors.append(f"every {key} item needs a non-empty id")
                continue
            accounted.append(item["id"])
    if len(set(accounted)) != len(accounted):
        errors.append("an item is accounted for more than once")
    if set(work_ids) != set(accounted):
        errors.append("coverage accounting has missing or unknown work items")
    for item in _list_field(data, "skipped", data["command"]):
        if not isinstance(item, dict):
            continue
        if item.get("code") not in SKIP_CODES:
            errors.append("skipped item has invalid code")
        evidence = item.get("evidence")
        if not isinstance(evidence, str) or not evidence:
            errors.append("skipped item needs evidence")
        elif evidence.startswith("lint:") and len(evidence) == len("lint:"):
            errors.append("skipped evidence needs a lint finding id")
        elif not evidence.startswith("lint:"):
            evidence_path = Path(evidence)
            if not evidence_path.is_absolute():
                evidence_path = root / evidence_path
            if not evidence_path.exists():
                errors.append(f"skipped evidence does not open: {evidence}")
        note = item.get("note")
        if not isinstance(note, str) or not note.strip():
            errors.append("skipped item needs a note")
    for item in _list_field(data, "out_of_scope", data["command"]):
        if not isinstance(item, dict) or not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append("out_of_scope item needs a reason")
    return errors


def _validate_filesystem(data: dict[str, Any], before: dict[str, Any], after: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    diff = snapshot_diff(before, after, root)
    if diff["raw_changed"]:
        errors.append("10_RAW changed: " + ", ".join(diff["raw_changed"]))
    reported = _result_paths(data)
    unreported = sorted(set(diff["wiki_changed"]) - reported)
    if unreported:
        errors.append("unreported Wiki writes: " + ", ".join(unreported))
    before_entries = before.get("entries", {})
    after_entries = after.get("entries", {})
    for relative in diff["wiki_changed"]:
        if relative not in before_entries or relative not in after_entries:
            continue
        path = root / relative
        if _append_only(relative):
            old = base64.b64decode(before.get("append_prefixes", {}).get(relative, ""))
            if not path.read_bytes().startswith(old):
                errors.append(f"append-only violation: {relative}")
        if _index_file(relative):
            old_hash = before.get("user_blocks", {}).get(relative)
            new_block = _user_block(path.read_bytes())
            new_hash = hashlib.sha256(new_block).hexdigest() if new_block is not None else None
            if old_hash != new_hash:
                errors.append(f"@user block changed: {relative}")
        if not _append_only(relative) and not _index_file(relative):
            text = path.read_text(encoding="utf-8", errors="replace")
            if relative.startswith("20_WIKI/entities/"):
                if "timeline" not in text:
                    errors.append(f"entity rewrite lacks timeline: {relative}")
            elif Path(relative).name.startswith("conflict-"):
                continue
            elif "## History" not in text:
                errors.append(f"rewrite lacks ## History: {relative}")
    return errors


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end is None:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"\'')
    return result


def _validate_synthesis(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    drafts = _list_field(data, "drafts", "synthesize")
    if len(drafts) > 1:
        errors.append("synthesize created more than one draft")
    for draft in drafts:
        path_value = _path_from_value(draft)
        if not path_value:
            errors.append("draft entry needs a path")
            continue
        path = root / path_value
        if not path.is_file():
            errors.append(f"draft file missing: {path_value}")
            continue
        front = _frontmatter(path)
        if front.get("auto_generated", "").lower() != "true":
            errors.append(f"draft lacks auto_generated: true: {path_value}")
        if front.get("status") != "draft":
            errors.append(f"draft status is not draft: {path_value}")
        text = path.read_text(encoding="utf-8", errors="replace")
        front_text = text.split("---", 2)[1] if text.startswith("---") and text.count("---") >= 2 else ""
        projects_section = re.search(r"(?ms)^projects:\s*\n(.*?)(?=^[A-Za-z_][\w-]*:|\Z)", front_text)
        project_count = len(re.findall(r"^\s+-\s+", projects_section.group(1), re.MULTILINE)) if projects_section else 0
        if project_count < 2:
            errors.append(f"draft needs at least two projects: {path_value}")
    for conflict in _list_field(data, "conflicts", "synthesize"):
        path_value = _path_from_value(conflict)
        if not path_value:
            continue
        path = root / path_value
        if path.is_file():
            front = _frontmatter(path)
            if front.get("type") != "conflict" or front.get("status") != "open":
                errors.append(f"conflict frontmatter invalid: {path_value}")
    return errors


def validate_result(data: dict[str, Any], command: str, run_id: str, week: str, lint_report: Path, before: dict[str, Any], after: dict[str, Any], root: Path = VAULT_ROOT) -> list[str]:
    errors = _validate_common(data, command, run_id, week, lint_report)
    if not errors:
        errors.extend(_validate_coverage(data, root))
        errors.extend(_validate_filesystem(data, before, after, root))
        if command == "synthesize":
            errors.extend(_validate_synthesis(data, root))
    return errors


def validate_audit(data: dict[str, Any], run_id: str, week: str) -> list[str]:
    errors: list[str] = []
    _require(data, ("schema_version", "run_id", "week", "verdict", "findings"), "audit")
    if data.get("schema_version") != 1:
        errors.append("audit schema_version must be 1")
    if data.get("run_id") != run_id or data.get("week") != week:
        errors.append("audit run_id/week mismatch")
    if data.get("verdict") not in {"pass", "fail"}:
        errors.append("audit verdict must be pass or fail")
    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("audit findings must be an array")
    else:
        for finding in findings:
            if not isinstance(finding, dict) or not all(isinstance(finding.get(key), str) and finding[key] for key in ("check", "severity", "evidence", "verdict")):
                errors.append("audit finding needs check, severity, evidence, verdict")
            else:
                finding_verdict = " ".join(finding["verdict"].casefold().replace("_", " ").split())
                positive_verdicts = {"pass", "passed", "confirmed", "ok", "not applicable"}
                negative_verdicts = {"fail", "failed", "unconfirmed", "uncertain", "unknown", "not confirmed", "not verified"}
                if finding_verdict not in positive_verdicts | negative_verdicts:
                    errors.append("audit finding verdict is unknown")
                elif finding_verdict in negative_verdicts:
                    errors.append(f"audit finding failed: {finding['check']}")
    if data.get("verdict") == "fail":
        errors.append("auditor verdict is fail")
    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate weekly reconcile/synthesize result JSON")
    parser.add_argument("--kind", choices=("reconcile", "synthesize", "audit"), required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--week", required=True)
    parser.add_argument("--lint-report", type=Path)
    parser.add_argument("--before", type=Path)
    parser.add_argument("--after", type=Path)
    parser.add_argument("--root", type=Path, default=VAULT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = load_json(args.result)
        if args.kind == "audit":
            errors = validate_audit(result, args.run_id, args.week)
        else:
            if not args.lint_report or not args.before or not args.after:
                raise GateError("result validation needs --lint-report, --before, and --after")
            before = load_json(args.before)
            after = load_json(args.after)
            errors = validate_result(result, args.kind, args.run_id, args.week, args.lint_report, before, after, args.root.resolve())
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        print(f"PASS: {args.kind} result validated")
        return 0
    except (GateError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
