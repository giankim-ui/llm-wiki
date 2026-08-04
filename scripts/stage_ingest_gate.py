"""Read-only Stage routing gate for the project ingest workflow.

The command deliberately has only three operations:

* ``inspect``: summarize pending entries from the /projects manifest.
* ``validate``: validate the Stage graph and synthesis-to-Stage assignment.
* ``consume``: mark a successfully ingested manifest as consumed.

The gate never edits vault Markdown. ``consume`` edits only the temporary
manifest written by /projects after it has successfully moved files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat as stat_module
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


VAULT_ROOT = Path(__file__).resolve().parents[1]
MODES_PATH = VAULT_ROOT / ".claude" / "commands" / "ingest-project-modes.json"
DEFAULT_STATE_DIR = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / "claude-projects-state"
DEFAULT_MANIFEST = DEFAULT_STATE_DIR / "moved.json"
ALLOWED_MODES = {"stage", "legacy"}
STAGE_FILE_RE = re.compile(r"^stage-(?P<number>\d+)-.+\.md$", re.IGNORECASE)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


class GateError(ValueError):
    """A configuration or manifest error that must stop before writing."""


def _json_load(path: Path) -> Any:
    def pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise GateError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except FileNotFoundError as exc:
        raise GateError(f"missing JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON {path}: line {exc.lineno}, column {exc.colno}") from exc


def load_modes(path: Path = MODES_PATH) -> dict[str, Any]:
    data = _json_load(path)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise GateError("mode JSON must have schema_version: 1")
    projects = data.get("projects")
    if not isinstance(projects, dict):
        raise GateError("mode JSON projects must be an object")
    for slug, mode in projects.items():
        if not isinstance(slug, str) or not slug.strip():
            raise GateError("mode JSON contains an invalid project slug")
        if mode not in ALLOWED_MODES:
            raise GateError(f"invalid mode for {slug}: {mode!r}")
    if data.get("default_mode") not in ALLOWED_MODES:
        raise GateError("mode JSON default_mode must be stage or legacy")
    return data


def mode_for_slug(slug: str, modes: dict[str, Any]) -> tuple[str, str | None]:
    projects = modes["projects"]
    if slug not in projects:
        return "legacy", f"unregistered project {slug!r}; safely using legacy mode"
    return projects[slug], None


def _resolve_path(value: str, root: Path = VAULT_ROOT) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = _json_load(path)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise GateError("manifest must have schema_version: 1")
    if not isinstance(data.get("run_id"), str) or not data["run_id"]:
        raise GateError("manifest run_id must be a non-empty string")
    if not isinstance(data.get("completed"), bool):
        raise GateError("manifest completed must be boolean")
    if "consumed_at" not in data or data["consumed_at"] is not None and not isinstance(data["consumed_at"], str):
        raise GateError("manifest consumed_at must be null or a string")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise GateError("manifest entries must be an array")
    seen_source: set[str] = set()
    seen_destination: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise GateError(f"manifest entry {index} must be an object")
        for key in ("source", "destination", "slug", "type"):
            if not isinstance(entry.get(key), str) or not entry[key]:
                raise GateError(f"manifest entry {index} missing string field {key}")
        source = str(_resolve_path(entry["source"]))
        destination = str(_resolve_path(entry["destination"]))
        if source in seen_source or destination in seen_destination:
            raise GateError(f"duplicate manifest entry at index {index}")
        seen_source.add(source)
        seen_destination.add(destination)
    return data


def _frontmatter_and_body(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[match.group(1)] = value
    return values, "\n".join(lines[end + 1 :])


def _summary_for(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = _frontmatter_and_body(text)
    title = frontmatter.get("title", "").strip()
    if not title:
        h1 = ""
        for line in body.splitlines():
            if line.startswith("# "):
                h1 = line[2:].strip()
                break
        title = h1
    if not title:
        title = path.stem

    lines = body.splitlines()
    summary_headings = {"요약", "summary", "개요", "결론"}
    candidate_lines: list[str] = []
    in_summary = False
    for line in lines:
        stripped = line.strip()
        heading = HEADING_RE.match(stripped)
        if heading:
            heading_name = re.sub(r"[*_`]", "", heading.group(1)).strip().lower()
            in_summary = heading_name in summary_headings
            continue
        if not stripped:
            if candidate_lines and in_summary:
                break
            continue
        if stripped.startswith("```") or stripped.startswith("|") or stripped.startswith(">"):
            continue
        if re.match(r"^[-*_]{3,}$", stripped) or stripped.startswith("- ") or stripped.startswith("* "):
            continue
        if in_summary or not candidate_lines:
            candidate_lines.append(re.sub(r"\s+", " ", stripped))
        if len(candidate_lines) >= 2:
            break
    summary = " ".join(candidate_lines).strip()
    if len(summary) > 240:
        summary = summary[:237].rstrip() + "..."
    return title, summary or "(요약 없음)"


def _manifest_entries(manifest: dict[str, Any] | None, modes: dict[str, Any], root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not manifest or not manifest["completed"] or manifest["consumed_at"] is not None:
        return [], []
    raw_root = (root / "10_RAW" / "projects").resolve()
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    for entry in manifest["entries"]:
        destination = _resolve_path(entry["destination"], root)
        slug = entry["slug"]
        mode, warning = mode_for_slug(slug, modes)
        if warning:
            warnings.append(warning)
        if mode != "stage":
            continue
        if not _is_within(destination, raw_root):
            warnings.append(f"ignored {entry['destination']}: destination missing or outside this Vault")
            continue
        try:
            metadata = destination.stat()
        except OSError:
            warnings.append(f"ignored {entry['destination']}: destination missing or outside this Vault")
            continue
        if not stat_module.S_ISREG(metadata.st_mode):
            warnings.append(f"ignored {entry['destination']}: destination missing or outside this Vault")
            continue
        entries.append({**entry, "_destination_path": destination, "_ctime_ns": metadata.st_ctime_ns})
    return entries, warnings


def _sort_entries(entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda e: (e.get("_ctime_ns", 0), str(e["_destination_path"]).lower()))


def _print_inspect(manifest: dict[str, Any] | None, entries: list[dict[str, Any]], warnings: list[str], root: Path) -> None:
    print(f"[stage-ingest] pending Stage files: {len(entries)}")
    if manifest:
        print(f"[stage-ingest] run_id: {manifest['run_id']}")
    for warning in warnings:
        print(f"[stage-ingest] WARNING: {warning}")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in _sort_entries(entries):
        grouped[entry["slug"]].append(entry)
    for slug, group in sorted(grouped.items()):
        hub = root / "20_WIKI" / "projects" / slug / f"{slug}.md"
        current = "unknown"
        current_title = ""
        if hub.exists():
            current = _frontmatter_and_body(hub.read_text(encoding="utf-8", errors="replace"))[0].get("current_stage", "unknown")
            current_number = _int_value(current)
            if current_number is not None:
                try:
                    stages = _stage_files(hub.parent)
                    if current_number in stages:
                        current_title = _summary_for(stages[current_number])[0]
                except (GateError, OSError, UnicodeError):
                    current_title = ""
        current_label = f"current Stage {current}"
        if current_title:
            current_label += f" — {current_title}"
        print(f"\n[{slug}] {current_label} — {len(group)} new file(s)")
        for entry in group:
            title, summary = _summary_for(entry["_destination_path"])
            print(f"- {title}: {summary}")


def _link_target(link: str) -> str:
    link = link.strip()
    if link.startswith("[[") and link.endswith("]]" ):
        link = link[2:-2]
    if link.strip().lower() in {"", "null", "none", "~"}:
        return ""
    target = link.split("|", 1)[0].split("#", 1)[0].strip().replace("\\", "/")
    target = target.rstrip("/").rsplit("/", 1)[-1]
    if target.lower().endswith(".md"):
        target = target[:-3]
    return target


def _wikilinks(text: str) -> set[str]:
    return {_link_target(match.group(1)) for match in WIKILINK_RE.finditer(text)}


def _int_value(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _stage_files(project_dir: Path) -> dict[int, Path]:
    result: dict[int, Path] = {}
    for path in project_dir.glob("stage-*.md"):
        match = STAGE_FILE_RE.match(path.name)
        if not match:
            continue
        number = int(match.group("number"))
        if number in result:
            raise GateError(f"duplicate Stage number {number}: {result[number].name}, {path.name}")
        result[number] = path
    return result


def _validate_project(slug: str, root: Path) -> list[str]:
    errors: list[str] = []
    project_dir = root / "20_WIKI" / "projects" / slug
    hub = project_dir / f"{slug}.md"
    if not hub.is_file():
        return [f"{slug}: hub missing: {hub.relative_to(root)}"]
    hub_front, hub_body = _frontmatter_and_body(hub.read_text(encoding="utf-8", errors="replace"))
    if hub_front.get("stage_enabled", "").lower() != "true":
        errors.append(f"{slug}: hub stage_enabled is not true")
    current_stage = _int_value(hub_front.get("current_stage"))
    if current_stage is None:
        errors.append(f"{slug}: hub current_stage is not an integer")
    if not hub_front.get("current_phase"):
        errors.append(f"{slug}: hub current_phase is missing")
    try:
        stages = _stage_files(project_dir)
    except GateError as exc:
        return [str(exc)]
    if not stages:
        return errors + [f"{slug}: STAGE_NOT_BOOTSTRAPPED (no stage notes found)"]
    expected = set(range(max(stages) + 1))
    if set(stages) != expected:
        errors.append(f"{slug}: Stage numbers are not continuous: {sorted(stages)}")
    active = []
    for number, path in sorted(stages.items()):
        front, body = _frontmatter_and_body(path.read_text(encoding="utf-8", errors="replace"))
        if front.get("status") == "active":
            active.append(number)
        if _int_value(front.get("stage")) != number:
            errors.append(f"{path.name}: frontmatter stage does not match filename")
        if front.get("project") != slug:
            errors.append(f"{path.name}: project must be {slug}")
        parent = _link_target(front.get("parent", ""))
        if parent != slug:
            errors.append(f"{path.name}: parent must link to {slug}")
        prev = _link_target(front.get("prev", "")) if front.get("prev") else ""
        next_stage = _link_target(front.get("next", "")) if front.get("next") else ""
        if number == 0:
            if prev:
                errors.append(f"{path.name}: Stage 0 must not have prev")
        elif prev != stages[number - 1].stem:
            errors.append(f"{path.name}: prev must link to {stages[number - 1].stem}")
        if number == max(stages):
            if next_stage:
                errors.append(f"{path.name}: final Stage must not have next")
        elif next_stage != stages[number + 1].stem:
            errors.append(f"{path.name}: next must link to {stages[number + 1].stem}")
    if len(active) != 1:
        errors.append(f"{slug}: expected exactly one active Stage, found {active}")
    if current_stage is not None and current_stage not in stages:
        errors.append(f"{slug}: current_stage {current_stage} does not exist")
    elif current_stage is not None and active != [current_stage]:
        errors.append(f"{slug}: current_stage {current_stage} is not the active Stage {active}")
    for path in stages.values():
        if path.stem not in _wikilinks(hub_body):
            errors.append(f"{slug}: hub Stage Map does not link {path.stem}")

    synthesis = project_dir / "synthesis.md"
    if synthesis.is_file():
        synthesis_links = _wikilinks(synthesis.read_text(encoding="utf-8", errors="replace"))
        stage_links: set[str] = set()
        stage_stems = {path.stem for path in stages.values()}
        for path in stages.values():
            stage_links.update(_wikilinks(path.read_text(encoding="utf-8", errors="replace")))
        ignored = {slug, "synthesis", "decisions", *stage_stems}
        missing = sorted(link for link in synthesis_links if link and link not in ignored and link not in stage_links)
        if missing:
            errors.append(f"{slug}: synthesis links not assigned to Stage flow: {', '.join(missing)}")
    else:
        errors.append(f"{slug}: synthesis.md missing")
    return errors


def validate_graph(root: Path = VAULT_ROOT, modes_path: Path = MODES_PATH, project: str | None = None) -> list[str]:
    modes = load_modes(modes_path)
    stage_projects = [project] if project else [slug for slug, mode in modes["projects"].items() if mode == "stage"]
    errors: list[str] = []
    for slug in stage_projects:
        mode, warning = mode_for_slug(slug, modes)
        if warning:
            errors.append(warning)
        if mode == "stage":
            errors.extend(_validate_project(slug, root))
    return errors


def _write_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def consume_manifest(path: Path, run_id: str | None = None) -> int:
    manifest = load_manifest(path)
    if manifest is None:
        print(f"[stage-ingest] no manifest: {path}")
        return 0
    if not manifest["completed"] or manifest["consumed_at"] is not None:
        print("[stage-ingest] manifest is incomplete or already consumed; no changes made")
        return 0
    if run_id and manifest["run_id"] != run_id:
        raise GateError(f"run_id mismatch: expected {run_id}, found {manifest['run_id']}")
    manifest["consumed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _write_manifest(path, manifest)
    print(f"[stage-ingest] consumed run {manifest['run_id']}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Stage ingest gate")
    parser.add_argument("--root", type=Path, default=VAULT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--modes", type=Path, default=MODES_PATH, help=argparse.SUPPRESS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect", help="summarize pending Stage files")
    validate = sub.add_parser("validate", help="validate Stage graph")
    validate.add_argument("--project", help="validate one project")
    consume = sub.add_parser("consume", help="mark a successful manifest consumed")
    consume.add_argument("--run-id", help="require this manifest run id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    modes_path = args.modes.resolve()
    manifest_path = args.manifest.resolve()
    try:
        modes = load_modes(modes_path)
        if args.command == "inspect":
            manifest = load_manifest(manifest_path)
            entries, warnings = _manifest_entries(manifest, modes, root)
            _print_inspect(manifest, entries, warnings, root)
            return 0
        if args.command == "validate":
            errors = validate_graph(root, modes_path, args.project)
            if errors:
                print("[stage-ingest] VALIDATION FAILED")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("[stage-ingest] VALIDATION PASSED")
            return 0
        return consume_manifest(manifest_path, args.run_id)
    except (GateError, OSError, UnicodeError) as exc:
        print(f"[stage-ingest] ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
