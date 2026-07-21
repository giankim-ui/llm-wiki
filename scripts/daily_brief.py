#!/usr/bin/env python3
"""Daily brief generator for LLM-Wiki vault (Schema v2.2).

Usage:
    python scripts/daily_brief.py [--backfill-log] [--skip-if-today] [--no-lint]
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(__file__).parent.parent

SCAN_DIRS: list[Path] = [
    VAULT_ROOT / "10_RAW" / "projects",
    VAULT_ROOT / "archive",
]

EventType = Literal["plan-version", "result", "handoff", "unknown"]

# LOG/synthesis 허용 이벤트 (CLAUDE.md BINDING 13개)
ALLOWED_LOG_EVENTS: frozenset[str] = frozenset({
    "decision", "plan-version", "result", "phase-start", "phase-complete",
    "status-change", "concept-extracted", "theme-extracted",
    "handoff", "query", "lint", "clipping", "research",
})
FORBIDDEN_LOG_EVENTS: frozenset[str] = frozenset({"ingest"})

_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.DOTALL)
# Handles both [[path|display]] and [[path\|display]] (Obsidian table-cell pipe escape)
_WIKILINK_DISPLAY_RE = re.compile(r"\[\[([^\]|\\]+?)(?:\\?\|([^\]]+))?\]\]")

_FILENAME_DATE_RE = re.compile(r"-(\d{6})(?:-v\d+\.\d+)?\.md$", re.IGNORECASE)

# path -> st_ctime 메모이즈 캐시. 동일 경로가 scan_yesterday/scan_active_plans/
# LOG-01 검사에서 반복 조회되므로 실제 stat() 호출은 경로당 1회로 제한한다.
_CTIME_CACHE: dict[Path, float] = {}


def get_ctime(path: Path) -> float:
    """path.stat().st_ctime 을 메모이즈해서 반환 (반복 stat 방지). OSError는 그대로 전파."""
    cached = _CTIME_CACHE.get(path)
    if cached is not None:
        return cached
    ctime = path.stat().st_ctime
    _CTIME_CACHE[path] = ctime
    return ctime


def file_effective_date(path: Path) -> date:
    """파일명 -YYMMDD 우선, 없으면 st_ctime(생성시각) fallback.

    Why: mtime은 vault에서 파일을 열기만 해도 갱신되어 어제 작성 파일을 오늘로 분류함.
    """
    m = _FILENAME_DATE_RE.search(path.name)
    if m:
        s = m.group(1)
        try:
            return date(2000 + int(s[:2]), int(s[2:4]), int(s[4:6]))
        except ValueError:
            pass
    try:
        return datetime.fromtimestamp(get_ctime(path)).date()
    except OSError:
        return datetime.fromtimestamp(path.stat().st_mtime).date()

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(order=False)
class VaultFile:
    path: Path
    mtime: datetime
    event_type: EventType
    title: str
    project: str
    status: str  # "active" | "done" | ""

    def sort_key(self) -> datetime:
        return self.mtime


@dataclass
class DailyContext:
    yesterday: date
    today: date
    yesterday_files: list[VaultFile] = field(default_factory=list)
    active_plans: list[VaultFile] = field(default_factory=list)
    projects: list[tuple[str, str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Frontmatter & content parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> dict[str, str]:
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}
    result: dict[str, str] = {}
    for raw_line in m.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, val = line.partition(":")
        if sep:
            result[key.strip()] = val.strip()
    return result


def extract_title(content: str, fm: dict[str, str], path: Path) -> str:
    if "title" in fm and fm["title"]:
        return fm["title"][:60]
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        raw = m.group(1)
        # Strip inline Plan:/Result:/Handoff: prefix
        raw = re.sub(r"^(Plan|Result|Handoff):\s*", "", raw, flags=re.IGNORECASE)
        return raw[:60]
    return path.stem[:60]


def classify_event(path: Path, fm: dict[str, str]) -> EventType:
    fm_type = fm.get("type", "").lower()
    name = path.name.lower()

    if fm_type == "plan" or name.startswith("plan"):
        return "plan-version"
    if fm_type == "result" or name.startswith("result"):
        return "result"
    if fm_type == "handoff" or name.startswith("handoff"):
        return "handoff"
    return "unknown"


def _infer_project(path: Path) -> str:
    parts = path.parts
    for i, part in enumerate(parts):
        if part in ("projects",) and i + 1 < len(parts):
            candidate = parts[i + 1]
            # Skip if candidate looks like a file
            if "." not in candidate:
                return candidate
    return ""


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def _read_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _collect_scan_files() -> list[Path]:
    """SCAN_DIRS(10_RAW/projects + archive) 전체 .md 파일을 1회 rglob으로 수집.

    scan_yesterday()와 scan_active_plans()가 동일 트리를 각자 rglob 하던 것을
    단일 워크로 합쳐 재사용한다 (파일시스템 중복 순회 방지).
    """
    files: list[Path] = []
    seen: set[Path] = set()
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob("*.md"):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            files.append(path)
    return files


def scan_yesterday(
    yesterday: date, _files: list[Path] | None = None
) -> list[VaultFile]:
    files: list[VaultFile] = []
    candidates = _files if _files is not None else _collect_scan_files()

    for path in candidates:
        if file_effective_date(path) != yesterday:
            continue
        try:
            # ctime = Windows 최초 생성 시각; mtime은 vault open만으로도 갱신됨
            mtime = datetime.fromtimestamp(get_ctime(path))
        except OSError:
            continue
        content = _read_safe(path)
        fm = parse_frontmatter(content)
        event_type = classify_event(path, fm)
        title = extract_title(content, fm, path)
        status = fm.get("status", "").strip().lower()
        project = fm.get("project", _infer_project(path))
        files.append(VaultFile(path, mtime, event_type, title, project, status))

    files.sort(key=lambda f: f.mtime)  # 오름차순 정렬 (ctime 기준)
    return files


def scan_active_plans(_files: list[Path] | None = None) -> list[VaultFile]:
    today = date.today()
    files: list[VaultFile] = []
    candidates = _files if _files is not None else _collect_scan_files()

    for path in candidates:
        name_lower = path.name.lower()
        # Only plan files
        if not name_lower.startswith("plan"):
            continue
        content = _read_safe(path)
        fm = parse_frontmatter(content)
        if fm.get("status", "").strip().lower() != "active":
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            mtime = datetime.now()
        title = extract_title(content, fm, path)
        project = fm.get("project", _infer_project(path))
        files.append(VaultFile(path, mtime, "plan-version", title, project, "active"))

    files.sort(key=lambda f: f.mtime, reverse=True)
    return files


def get_active_projects() -> list[tuple[str, str, str]]:
    index_candidates = [
        VAULT_ROOT / "20_WIKI" / "projects" / "projects-INDEX.md",
        VAULT_ROOT / "INDEX.md",
    ]
    for idx_path in index_candidates:
        if not idx_path.exists():
            continue
        content = _read_safe(idx_path)
        results: list[tuple[str, str, str]] = []
        for raw_line in content.splitlines():
            if "|" not in raw_line:
                continue
            if "active" not in raw_line.lower():
                continue
            # Normalize Obsidian \| pipe-escape so wikilinks aren't split
            normalized = raw_line.replace(r"\|", "\x00")
            cells = [c.strip() for c in normalized.split("|") if c.strip()]
            if len(cells) < 3:
                continue
            raw_name = cells[0].replace("\x00", "|")
            # Extract display name from [[path|display]] or [[path\|display]] or [[slug]]
            wm = _WIKILINK_DISPLAY_RE.search(raw_name)
            if wm:
                # group(2) = display name after pipe; group(1) = path (last segment as fallback)
                display = wm.group(2) or wm.group(1).split("/")[-1]
                project_name = display.strip()
            else:
                project_name = raw_name.strip("[] ")
            # After normalization: cells[1]=Status, cells[2]=LastActivity, cells[3]=Phase
            status_cell = cells[1].replace("\x00", "|") if len(cells) > 1 else ""
            last_activity = cells[2].replace("\x00", "|") if len(cells) > 2 else ""
            phase = cells[3].replace("\x00", "|") if len(cells) > 3 else ""
            if "active" not in status_cell.lower():
                continue
            results.append((project_name, phase, last_activity))
        if results:
            return results
    return []


# ---------------------------------------------------------------------------
# Relative time label
# ---------------------------------------------------------------------------

def relative_time_label(mtime: datetime, today: date) -> str:
    d = mtime.date()
    hm = mtime.strftime("%H:%M")
    if d == today:
        return f"오늘 {hm}"
    if d == today - timedelta(days=1):
        return f"어제 {hm}"
    return f"{d.strftime('%m-%d')} {hm}"


# ---------------------------------------------------------------------------
# Markdown table builders
# ---------------------------------------------------------------------------

def _escape_pipe(s: str) -> str:
    return s.replace("|", "｜")


def format_yesterday_table(files: list[VaultFile]) -> str:
    if not files:
        return "_어제 기록된 이벤트 없음_\n"
    rows = ["| 시간 | 이벤트 | 파일 | 1줄 요약 |", "|---|---|---|---|"]
    for f in files:
        hm = f.mtime.strftime("%H:%M")
        stem = f.path.stem
        summary = _escape_pipe(f.title)
        rows.append(f"| {hm} | {f.event_type} | [[{stem}]] | {summary} |")
    return "\n".join(rows) + "\n"


def format_active_plans_table(active: list[VaultFile], today: date) -> str:
    if not active:
        return "_미완 plan 없음_\n"
    rows = ["| 마지막 활동 | Plan | Project | 다음 작업 |", "|---|---|---|---|"]
    for f in active:
        last_label = relative_time_label(f.mtime, today)
        stem = f.path.stem
        project = _escape_pipe(f.project) if f.project else "—"
        rows.append(f"| {last_label} | [[{stem}]] | {project} | — |")
    return "\n".join(rows) + "\n"


def format_projects_table(projects: list[tuple[str, str, str]]) -> str:
    if not projects:
        return "_진행 중 프로젝트 없음_\n"
    rows = ["| Project | Phase | Last Activity |", "|---|---|---|"]
    for name, phase, last in projects:
        rows.append(f"| [[{name}]] | {_escape_pipe(phase)} | {last} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------------------
# DAILY.md content builder
# ---------------------------------------------------------------------------

_WEEKDAY_KO = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _has_matching_result(plan: VaultFile) -> bool:
    """plan-{desc}-YYMMDD 에 대응하는 result-{desc}-*.md 가 results/ 에 존재하면 True."""
    stem = plan.path.stem
    desc = re.sub(r"^plan-", "", stem)
    desc = re.sub(r"-\d{6}(?:-v\d+\.\d+)?$", "", desc)
    if not desc or desc.isdigit():
        return False
    parts = list(plan.path.parts)
    try:
        proj_idx = parts.index("projects")
        slug = parts[proj_idx + 1]
    except (ValueError, IndexError):
        slug = plan.project or ""
    if not slug:
        return False
    results_dir = VAULT_ROOT / "10_RAW" / "projects" / slug / "results"
    # desc 뒤 하이픈 필수 → prefix-collision 방지 (result-report-role vs result-report-roles)
    return any(
        p for p in results_dir.glob(f"result-{desc}-*.md")
        if p.stem.startswith(f"result-{desc}-")
    )


def build_summary_lines(ctx: DailyContext) -> tuple[str, str]:
    last_event = ctx.yesterday_files[-1] if ctx.yesterday_files else None
    last_plan = ctx.active_plans[0] if ctx.active_plans else None

    if last_event:
        flow_line = (
            f"마지막 작업: `{last_event.path.stem}` ({last_event.event_type})"
            f" — {last_event.title}"
        )
    else:
        flow_line = "어제 기록된 이벤트 없음"

    if last_plan:
        hint = " (result 있음 — done 처리 누락 가능)" if _has_matching_result(last_plan) else ""
        start_line = (
            f"[[{last_plan.path.stem}]] 구현 대기"
            + (f" ({last_plan.project})" if last_plan.project else "")
            + hint
        )
    else:
        start_line = "미완 plan 없음"

    return flow_line, start_line


def build_daily_md(ctx: DailyContext) -> str:
    now = datetime.now()
    updated = now.strftime("%Y-%m-%d %H:%M")
    ystr = ctx.yesterday.strftime("%Y-%m-%d")
    tstr = ctx.today.strftime("%Y-%m-%d")
    tday_name = _WEEKDAY_KO[ctx.today.weekday()]

    flow_line, start_line = build_summary_lines(ctx)

    return f"""---
type: daily-brief
updated: {updated}
scope: root
---

# Daily Brief — {tstr} ({tday_name})

## 한 줄 요약
- **어제 흐름**: {flow_line}
- **오늘 시작점**: {start_line}

## 어제 ({ystr})
{format_yesterday_table(ctx.yesterday_files)}
## 오늘 ({tstr}) — 미완 plan (status:active)
{format_active_plans_table(ctx.active_plans, ctx.today)}
## 진행 중 프로젝트
{format_projects_table(ctx.projects)}"""


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def write_with_retry(path: Path, content: str, retries: int = 3, delay: float = 1.0) -> bool:
    for attempt in range(retries):
        try:
            path.write_text(content, encoding="utf-8")
            return True
        except OSError as e:
            if attempt < retries - 1:
                print(
                    f"[경고] {path.name} 쓰기 실패 (시도 {attempt + 1}/{retries}): {e}",
                    file=sys.stderr,
                )
                time.sleep(delay)
            else:
                print(f"[오류] {path.name} 쓰기 최종 실패: {e}", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# LOG.md backfill
# ---------------------------------------------------------------------------

def backfill_log(log_path: Path, ctx: DailyContext) -> None:
    if not ctx.yesterday_files:
        print("[LOG.md] 어제 파일 없음 - backfill 불필요")
        return

    existing = _read_safe(log_path) if log_path.exists() else ""

    # Collect already-logged timestamps (HH:MM on yesterday's date)
    ystr = ctx.yesterday.strftime("%Y-%m-%d")
    existing_timestamps: set[str] = set()
    for m in re.finditer(
        rf"\[{re.escape(ystr)}\s+(\d{{2}}:\d{{2}})\]", existing
    ):
        existing_timestamps.add(m.group(1))

    new_entries: list[str] = []
    for f in ctx.yesterday_files:
        hm = f.mtime.strftime("%H:%M")
        if hm in existing_timestamps:
            continue
        stem = f.path.stem
        summary = f.title[:60]
        new_entries.append(
            f"- [{ystr} {hm}] {f.event_type} | {stem} | {summary}"
        )

    if not new_entries:
        print("[LOG.md] 모든 항목이 이미 기록됨 - backfill 불필요")
        return

    # Insert after the existing 5/12 ingest entry if possible, otherwise append
    day_header = f"\n## [{ystr}] — {ystr} 작업 backfill\n"
    if day_header.strip() not in existing:
        new_block = day_header + "\n".join(new_entries) + "\n"
    else:
        new_block = "\n".join(new_entries) + "\n"

    new_content = existing.rstrip() + "\n" + new_block
    if write_with_retry(log_path, new_content):
        print(f"[LOG.md] {len(new_entries)}건 backfill 완료")


# ---------------------------------------------------------------------------
# LOG-01 날짜 정합성 검사
# ---------------------------------------------------------------------------

_LOG_SECTION_RE = re.compile(r"^(?:<[^>]+>)?##\s+(\d{4}-\d{2}-\d{2})\b")
_LOG_WIKILINK_RE = re.compile(r"\[\[([^\]|\\]+?)(?:\\?\|[^\]]*)?\]\]")


def _build_raw_index(raw_root: Path) -> dict[str, Path]:
    """10_RAW/projects 전체 .md 파일을 stem→path 딕셔너리로 인덱싱 (1회)."""
    index: dict[str, Path] = {}
    if not raw_root.exists():
        return index
    for p in raw_root.rglob("*.md"):
        if p.is_file():
            index[p.stem] = p
    return index


_LOG01_SKIP_EVENTS: frozenset[str] = frozenset({
    "status-change", "query", "lint", "phase-start", "phase-complete", "decision",
})


def check_log_date_mismatches(
    log_path: Path, raw_root: Path
) -> list[tuple[str, str, str]]:
    """projects-LOG.md 행의 [[파일]] ctime 날짜와 섹션 헤더 날짜가 다른 항목 반환.

    Returns list of (section_date, filename_stem, actual_ctime_date).
    LOG-01 Gotcha 기반: 섹션 헤더 = 파일 effective_date여야 함.
    status-change/query/lint 등 point-in-time 이벤트는 체크 대상 제외.
    """
    content = _read_safe(log_path)
    raw_index = _build_raw_index(raw_root)
    mismatches: list[tuple[str, str, str]] = []
    current_section_date: date | None = None

    for line in content.splitlines():
        sec_m = _LOG_SECTION_RE.match(line)
        if sec_m:
            try:
                current_section_date = date.fromisoformat(sec_m.group(1))
            except ValueError:
                current_section_date = None
            continue

        if current_section_date is None or "|" not in line:
            continue

        # point-in-time 이벤트(status-change 등)는 발생일 기준이므로 skip
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) >= 2 and cells[1].lower() in _LOG01_SKIP_EVENTS:
            continue

        wm = _LOG_WIKILINK_RE.search(line)
        if not wm:
            continue

        stem = wm.group(1).strip()
        # 폴더 경로 참조(10_RAW/projects 등) 제외
        if "/" in stem or "\\" in stem:
            continue

        actual_path = raw_index.get(stem)
        if actual_path is None:
            continue

        effective_date = file_effective_date(actual_path)

        if effective_date != current_section_date:
            mismatches.append((
                current_section_date.isoformat(),
                stem,
                effective_date.isoformat(),
            ))

    return mismatches


# ---------------------------------------------------------------------------
# LOG-02 금지 이벤트 검사
# ---------------------------------------------------------------------------

_TABLE_EVENT_RE = re.compile(r"^\|\s*[^|]+\|\s*(\S+)\s*\|")


def _build_log_content_cache(paths: list[Path]) -> dict[Path, str]:
    """LOG-02/LOG-03이 공유하는 파일 텍스트를 1회만 읽어 캐시한다.

    이전에는 각 검사가 동일 synthesis.md/LOG.md 파일을 독립적으로 read_text() 했다.
    """
    cache: dict[Path, str] = {}
    for path in paths:
        if not path.exists():
            continue
        try:
            cache[path] = path.read_text(encoding="utf-8")
        except OSError:
            continue
    return cache


def check_forbidden_events(
    paths: list[Path],
    content_cache: dict[Path, str] | None = None,
) -> list[tuple[str, int, str]]:
    """LOG.md / *-LOG.md / synthesis.md 표 행에서 금지 이벤트를 탐지한다.

    Returns list of (file_path_str, line_no, event_value).
    LOG-02: `ingest` 등 BINDING 어휘 외 이벤트 사용 방지.
    """
    violations: list[tuple[str, int, str]] = []
    for path in paths:
        if content_cache is not None:
            text = content_cache.get(path)
            if text is None:
                continue
            lines = text.splitlines()
        else:
            if not path.exists():
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
        for lineno, line in enumerate(lines, 1):
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6 and parts[0] == "" and parts[-1] == "":
                event = parts[2]
                if event and not set(event) <= set("-") and event in FORBIDDEN_LOG_EVENTS:
                    violations.append((str(path), lineno, event))
    return violations


# ---------------------------------------------------------------------------
# LOG-03 날짜/시간 정렬 검사
# ---------------------------------------------------------------------------

_LOG_TIME_RE = re.compile(r"^([0-2][0-9]:[0-5][0-9])$")
_LOG_BOLD_SUBHEADER_RE = re.compile(r"^\*\*(.+?)\*\*$")


def check_log_sort_order(
    paths: list[Path],
    content_cache: dict[Path, str] | None = None,
) -> list[tuple[str, str, str]]:
    """LOG.md / *-LOG.md 표 형식 날짜 섹션의 정렬 붕괴를 탐지한다.

    Returns list of (file_path_str, kind, detail).
    kind:
      - "dup-header": 동일 `## YYYY-MM-DD` 헤더가 파일 내 2회 이상 등장 (분산 append 재발 징후)
      - "header-order": `## YYYY-MM-DD` 헤더가 내림차순이 아님
      - "time-order": 같은 섹션 내 표 행 시간이 오름차순이 아님
    2026-07-16 LOG.md/projects-LOG.md 날짜정렬 붕괴(동일 날짜 헤더 최대 3회 분산) 재발 방지용.
    """
    violations: list[tuple[str, str, str]] = []
    for path in paths:
        if content_cache is not None:
            text = content_cache.get(path)
            if text is None:
                continue
            lines = text.splitlines()
        else:
            if not path.exists():
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue

        seen_dates: dict[str, int] = {}
        header_dates: list[tuple[str, int]] = []
        current_date: str | None = None
        prev_time: str | None = None

        for lineno, line in enumerate(lines, 1):
            m = _LOG_SECTION_RE.match(line)
            if m:
                d = m.group(1)
                if d in seen_dates:
                    violations.append((
                        str(path), "dup-header",
                        f"L{lineno}: ## {d} 중복 (첫 등장 L{seen_dates[d]})",
                    ))
                else:
                    seen_dates[d] = lineno
                header_dates.append((d, lineno))
                current_date = d
                prev_time = None
                continue

            if _LOG_BOLD_SUBHEADER_RE.match(line.strip()):
                # 프로젝트 slug 하위 소제목(projects-LOG.md) — 독립 미니테이블 시작
                prev_time = None
                continue

            if current_date is None or "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if parts and parts[0] == "":
                parts = parts[1:]
            if parts and parts[-1] == "":
                parts = parts[:-1]
            if not parts:
                continue

            t = parts[0]
            if not _LOG_TIME_RE.match(t):
                continue  # '—' 또는 헤더/구분 행은 시간정렬 체크 제외

            if prev_time is not None and t < prev_time:
                violations.append((
                    str(path), "time-order",
                    f"L{lineno}: {t} < 이전 {prev_time} (섹션 ## {current_date})",
                ))
            prev_time = t

        for i in range(1, len(header_dates)):
            prev_d, prev_ln = header_dates[i - 1]
            cur_d, cur_ln = header_dates[i]
            if cur_d > prev_d:
                violations.append((
                    str(path), "header-order",
                    f"L{cur_ln}: ## {cur_d} 가 이전 헤더(L{prev_ln} ## {prev_d})보다 최신 — 내림차순 위반",
                ))

    return violations


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM-Wiki 출근 브리핑 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backfill-log",
        action="store_true",
        help="어제 누락 LOG.md entries를 backfill",
    )
    parser.add_argument(
        "--no-lint",
        action="store_true",
        help="LOG-01/02/03 정합성 검사 콘솔 출력을 생략 (DAILY.md는 항상 그대로 재생성됨)",
    )
    args = parser.parse_args()

    today = date.today()
    yesterday = today - timedelta(days=1)
    daily_path = VAULT_ROOT / "DAILY.md"

    scan_files = _collect_scan_files()

    print(f"[스캔] 어제({yesterday}) vault 파일 탐색 중...")
    yesterday_files = scan_yesterday(yesterday, scan_files)
    print(f"  → {len(yesterday_files)}건 발견")

    print("[스캔] 미완 plan (status:active) 탐색 중...")
    active_plans = scan_active_plans(scan_files)
    print(f"  → {len(active_plans)}건 발견")

    print("[스캔] 진행 중 프로젝트 목록 로드 중...")
    projects = get_active_projects()
    print(f"  → {len(projects)}건 발견")

    ctx = DailyContext(
        yesterday=yesterday,
        today=today,
        yesterday_files=yesterday_files,
        active_plans=active_plans,
        projects=projects,
    )

    if not args.no_lint:
        # LOG-01 날짜 정합성 검사
        log_path = VAULT_ROOT / "20_WIKI" / "projects" / "projects-LOG.md"
        raw_root = VAULT_ROOT / "10_RAW" / "projects"
        if log_path.exists():
            print("[점검] LOG 날짜 정합성 검사 (LOG-01) ...")
            mismatches = check_log_date_mismatches(log_path, raw_root)
            if mismatches:
                print(f"  [!] LOG-01 불일치 {len(mismatches)}건:")
                for sec_date, fname, ctime_date in mismatches[:10]:  # 최대 10건 표시
                    print(f"    [[{fname}]] 섹션={sec_date} / ctime={ctime_date}")
                if len(mismatches) > 10:
                    print(f"    ... 외 {len(mismatches) - 10}건")
            else:
                print("  ✓ LOG-01 정합성 OK")

        # LOG-02 금지 이벤트 검사
        log02_targets: list[Path] = [
            VAULT_ROOT / "LOG.md",
            VAULT_ROOT / "20_WIKI" / "projects" / "projects-LOG.md",
        ]
        for p in (VAULT_ROOT / "20_WIKI").rglob("synthesis.md"):
            log02_targets.append(p)
        # synthesis.md/LOG.md는 LOG-02와 LOG-03가 공유하므로 1회만 읽어 캐시한다
        log_content_cache = _build_log_content_cache(log02_targets)

        print("[점검] 금지 이벤트 검사 (LOG-02) ...")
        violations = check_forbidden_events(log02_targets, log_content_cache)
        if violations:
            print(f"  [!] LOG-02 금지 이벤트 {len(violations)}건:")
            for fpath, lineno, event in violations[:10]:
                try:
                    short = Path(fpath).relative_to(VAULT_ROOT)
                except ValueError:
                    short = Path(fpath).name
                print(f"    {short}:{lineno} event=`{event}`")
            if len(violations) > 10:
                print(f"    ... 외 {len(violations) - 10}건")
        else:
            print("  OK LOG-02 금지 이벤트 없음")

        # LOG-03 날짜/시간 정렬 검사
        print("[점검] 날짜/시간 정렬 검사 (LOG-03) ...")
        sort_violations = check_log_sort_order(log02_targets, log_content_cache)
        if sort_violations:
            print(f"  [!] LOG-03 정렬 위반 {len(sort_violations)}건:")
            for fpath, kind, detail in sort_violations[:10]:
                try:
                    short = Path(fpath).relative_to(VAULT_ROOT)
                except ValueError:
                    short = Path(fpath).name
                print(f"    {short} [{kind}] {detail}")
            if len(sort_violations) > 10:
                print(f"    ... 외 {len(sort_violations) - 10}건")
        else:
            print("  OK LOG-03 정렬 위반 없음")

    content = build_daily_md(ctx)

    print(f"[쓰기] DAILY.md → {daily_path}")
    ok = write_with_retry(daily_path, content)
    if ok:
        print("[완료] DAILY.md 갱신 완료")

    if args.backfill_log:
        log_path = VAULT_ROOT / "LOG.md"
        backfill_log(log_path, ctx)


if __name__ == "__main__":
    main()
