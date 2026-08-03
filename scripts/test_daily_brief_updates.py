"""TDD 드라이런: 2026-06-29 세션 업데이트 검증 테스트.

검증 대상:
  - _has_matching_result()
  - build_summary_lines() stale hint
  - check_log_date_mismatches() file_effective_date + skip events
  - plan-hr-cost-mvp-260625 status=done
  - R.S.md §7.5 존재
"""

from __future__ import annotations

import sys
import re
import textwrap
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

VAULT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import daily_brief as db


# ---------------------------------------------------------------------------
# 픽스처 헬퍼
# ---------------------------------------------------------------------------

def _make_vault_file(stem: str, slug: str, status: str = "active") -> db.VaultFile:
    """테스트용 VaultFile 생성."""
    fake_path = VAULT_ROOT / "10_RAW" / "projects" / slug / "plans" / f"{stem}.md"
    return db.VaultFile(
        path=fake_path,
        mtime=datetime(2026, 6, 25, 10, 0),
        event_type="plan-version",
        title="Test Plan",
        project=slug,
        status=status,
    )


# ---------------------------------------------------------------------------
# US-001: _has_matching_result() 함수 로직
# ---------------------------------------------------------------------------

class TestHasMatchingResult:

    def test_desc_extraction_from_stem(self, tmp_path: Path, monkeypatch):
        """plan-hr-cost-mvp-260625 → desc=hr-cost-mvp 추출 후 result 파일 탐색."""
        # _has_matching_result는 VAULT_ROOT/10_RAW/projects/{slug}/results/ 탐색
        results_dir = tmp_path / "10_RAW" / "projects" / "anlyz-hrIndexData" / "results"
        results_dir.mkdir(parents=True)
        (results_dir / "result-hr-cost-mvp-260625-v1.0.md").write_text("---\ntype: result\n---\n")

        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)

        vf = _make_vault_file("plan-hr-cost-mvp-260625", "anlyz-hrIndexData")
        assert db._has_matching_result(vf) is True

    def test_no_result_returns_false(self, tmp_path: Path, monkeypatch):
        """results/ 폴더 자체가 없으면 False."""
        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
        vf = _make_vault_file("plan-memo-debug-260622", "okr-supa-memo-debug")
        assert db._has_matching_result(vf) is False

    def test_slug_inferred_from_path(self, tmp_path: Path, monkeypatch):
        """경로에서 slug 추출: 10_RAW/projects/{slug}/plans/ 구조."""
        results_dir = tmp_path / "10_RAW" / "projects" / "meeting-db" / "results"
        results_dir.mkdir(parents=True)
        (results_dir / "result-todo-ui-v2-260601.md").write_text("---\ntype: result\n---\n")

        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)

        fake_path = tmp_path / "projects" / "meeting-db" / "plans" / "plan-todo-ui-v2-260529.md"
        vf = db.VaultFile(
            path=fake_path, mtime=datetime(2026, 5, 29, 10, 0),
            event_type="plan-version", title="test", project="meeting-db", status="active",
        )
        assert db._has_matching_result(vf) is True

    def test_empty_desc_returns_false(self, tmp_path: Path, monkeypatch):
        """desc가 비면 False (plan-.md 같은 이상 케이스)."""
        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
        fake_path = tmp_path / "projects" / "foo" / "plans" / "plan-260625.md"
        vf = db.VaultFile(
            path=fake_path, mtime=datetime.now(),
            event_type="plan-version", title="", project="foo", status="active",
        )
        assert db._has_matching_result(vf) is False


# ---------------------------------------------------------------------------
# US-002: build_summary_lines() stale hint
# ---------------------------------------------------------------------------

class TestBuildSummaryLinesStaleHint:

    def _ctx_with_plan(self, vf: db.VaultFile) -> db.DailyContext:
        ctx = db.DailyContext(yesterday=date(2026, 6, 28), today=date(2026, 6, 29))
        ctx.active_plans = [vf]
        return ctx

    def test_hint_present_when_result_exists(self, tmp_path: Path, monkeypatch):
        """matching result 있으면 hint 문자열 포함."""
        results_dir = tmp_path / "10_RAW" / "projects" / "anlyz-hrIndexData" / "results"
        results_dir.mkdir(parents=True)
        (results_dir / "result-hr-cost-mvp-260625-v1.0.md").write_text("---\ntype: result\n---\n")
        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)

        vf = _make_vault_file("plan-hr-cost-mvp-260625", "anlyz-hrIndexData")
        _, start_line = db.build_summary_lines(self._ctx_with_plan(vf))

        assert "result 있음" in start_line
        assert "done 처리 누락 가능" in start_line

    def test_no_hint_when_no_result(self, tmp_path: Path, monkeypatch):
        """matching result 없으면 hint 없음."""
        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
        vf = _make_vault_file("plan-memo-debug-260622", "okr-supa-memo-debug")
        _, start_line = db.build_summary_lines(self._ctx_with_plan(vf))

        assert "result 있음" not in start_line
        assert "done 처리 누락 가능" not in start_line

    def test_start_line_base_format_preserved(self, tmp_path: Path, monkeypatch):
        """hint 없는 경우 기존 형식([[stem]] 구현 대기 (project)) 유지."""
        monkeypatch.setattr(db, "VAULT_ROOT", tmp_path)
        vf = _make_vault_file("plan-memo-debug-260622", "myslug")
        _, start_line = db.build_summary_lines(self._ctx_with_plan(vf))

        assert "[[plan-memo-debug-260622]]" in start_line
        assert "구현 대기" in start_line


# ---------------------------------------------------------------------------
# US-003 + US-004: LOG-01 file_effective_date + skip events
# ---------------------------------------------------------------------------

class TestLog01Check:

    def _write_log(self, path: Path, content: str):
        path.write_text(textwrap.dedent(content), encoding="utf-8")

    def test_filename_date_used_over_ctime(self, tmp_path: Path):
        """파일명 -YYMMDD가 ctime보다 우선 사용됨 (file_effective_date 검증)."""
        raw_root = tmp_path / "projects"
        plans_dir = raw_root / "anlyz-hrIndexData" / "plans"
        plans_dir.mkdir(parents=True)
        plan_file = plans_dir / "plan-hr-cost-mvp-260625.md"
        plan_file.write_text("---\nstatus: done\n---\n")

        log_path = tmp_path / "projects-LOG.md"
        self._write_log(log_path, """
            ---
            type: log
            ---
            ## 2026-06-25

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | — | plan-version | [[plan-hr-cost-mvp-260625]] | HR MVP plan |
        """)

        mismatches = db.check_log_date_mismatches(log_path, raw_root)
        stems = [m[1] for m in mismatches]
        assert "plan-hr-cost-mvp-260625" not in stems, (
            f"file_effective_date로 날짜 추출 시 불일치 없어야 함. mismatches={mismatches}"
        )

    def test_status_change_event_skipped(self, tmp_path: Path):
        """status-change 이벤트 행은 LOG-01 체크에서 제외."""
        raw_root = tmp_path / "projects"
        plans_dir = raw_root / "anlyz-hrIndexData" / "plans"
        plans_dir.mkdir(parents=True)
        plan_file = plans_dir / "plan-hr-cost-mvp-260625.md"
        plan_file.write_text("---\nstatus: done\n---\n")

        log_path = tmp_path / "projects-LOG.md"
        self._write_log(log_path, """
            ---
            type: log
            ---
            ## 2026-06-29

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 14:36 | status-change | [[plan-hr-cost-mvp-260625]] | status active → done |
        """)

        mismatches = db.check_log_date_mismatches(log_path, raw_root)
        stems = [m[1] for m in mismatches]
        assert "plan-hr-cost-mvp-260625" not in stems, (
            f"status-change 이벤트는 skip되어야 함. mismatches={mismatches}"
        )

    def test_skip_events_constant_contains_required(self):
        """_LOG01_SKIP_EVENTS에 status-change 등 point-in-time 이벤트 포함."""
        required = {"status-change", "query", "lint", "phase-start", "phase-complete"}
        missing = required - db._LOG01_SKIP_EVENTS
        assert not missing, f"_LOG01_SKIP_EVENTS에 누락: {missing}"


class TestLog03SortOrder:
    """2026-07-16 LOG.md/projects-LOG.md 날짜정렬 붕괴 재발 방지 (check_log_sort_order)."""

    def _write(self, path: Path, content: str):
        path.write_text(textwrap.dedent(content), encoding="utf-8")

    def test_duplicate_header_detected(self, tmp_path: Path):
        log_path = tmp_path / "LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-07-08

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 10:00 | result | [[a]] | a |

            ## 2026-07-07

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 09:00 | result | [[b]] | b |

            ## 2026-07-08

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 11:00 | result | [[c]] | c |
        """)
        violations = db.check_log_sort_order([log_path])
        kinds = [v[1] for v in violations]
        assert "dup-header" in kinds, f"중복 헤더 미탐지: {violations}"

    def test_header_descending_violation_detected(self, tmp_path: Path):
        log_path = tmp_path / "LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-07-07

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 09:00 | result | [[a]] | a |

            ## 2026-07-08

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 10:00 | result | [[b]] | b |
        """)
        violations = db.check_log_sort_order([log_path])
        kinds = [v[1] for v in violations]
        assert "header-order" in kinds, f"내림차순 위반 미탐지: {violations}"

    def test_time_ascending_violation_detected(self, tmp_path: Path):
        log_path = tmp_path / "LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-07-08

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 15:00 | result | [[a]] | a |
            | 10:00 | result | [[b]] | b |
        """)
        violations = db.check_log_sort_order([log_path])
        kinds = [v[1] for v in violations]
        assert "time-order" in kinds, f"시간 오름차순 위반 미탐지: {violations}"

    def test_em_dash_time_not_flagged(self, tmp_path: Path):
        """'—' (시간불명) 행은 시간정렬 체크에서 제외되어야 함."""
        log_path = tmp_path / "LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-06-25

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | — | plan-version | [[a]] | a |
            | 18:02 | result | [[b]] | b |
        """)
        violations = db.check_log_sort_order([log_path])
        assert violations == [], f"em-dash 행 오탐: {violations}"

    def test_bold_subheader_resets_time_sequence(self, tmp_path: Path):
        """projects-LOG.md의 **slug** 소제목마다 독립 미니테이블 — 시간 리셋되어야 함(오탐 방지)."""
        log_path = tmp_path / "projects-LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-06-30

            **anlyz-hrIndexData**

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 09:38 | plan-version | [[a]] | a |
            | 18:20 | plan-version | [[b]] | b |

            **okr-matrix**

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 17:30 | plan-version | [[c]] | c |
            | 18:14 | plan-version | [[d]] | d |
        """)
        violations = db.check_log_sort_order([log_path])
        assert violations == [], f"slug 소제목 리셋 실패로 오탐 발생: {violations}"

    def test_clean_file_no_violations(self, tmp_path: Path):
        log_path = tmp_path / "LOG.md"
        self._write(log_path, """
            ---
            type: log
            ---
            ## 2026-07-08

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 10:00 | result | [[a]] | a |
            | 11:00 | result | [[b]] | b |

            ## 2026-07-07

            | 시간 | 이벤트 | 파일 | 1줄 요약 |
            |---|---|---|---|
            | 09:00 | result | [[c]] | c |
        """)
        violations = db.check_log_sort_order([log_path])
        assert violations == [], f"정상 파일에서 오탐: {violations}"


# ---------------------------------------------------------------------------

class TestActivePlansCompact:

    def test_visible_limit_keeps_newest_fifteen(self):
        today = date(2026, 7, 31)
        active: list[db.VaultFile] = []
        for idx in range(16):
            vf = _make_vault_file(f"plan-noise-{idx:02d}-260731", "anlyz-hrIndexData")
            vf.mtime = datetime(2026, 7, 31, 12, 0) - timedelta(days=idx)
            active.append(vf)

        table = db.format_active_plans_table(active, today)

        assert "Older active plans (1)" in table
        assert table.count("[[plan-noise-") == 16
        assert "plan-noise-15-260731" in table

    def test_plans_older_than_30_days_collapse(self):
        today = date(2026, 7, 31)
        active: list[db.VaultFile] = []
        for idx in range(15):
            vf = _make_vault_file(f"plan-recent-{idx:02d}-260731", "anlyz-hrIndexData")
            vf.mtime = datetime(2026, 7, 31, 12, 0) - timedelta(days=idx)
            active.append(vf)

        old = _make_vault_file("plan-old-260701", "anlyz-hrIndexData")
        old.mtime = datetime(2026, 7, 1, 12, 0)
        active.append(old)

        table = db.format_active_plans_table(active, today)

        assert "Older active plans (1)" in table
        assert "plan-old-260701" in table
        assert table.index("plan-old-260701") > table.index("<details>")# US-005: plan-hr-cost-mvp-260625 status=done 실제 파일 검증
# ---------------------------------------------------------------------------

class TestPlanStatusDone:

    def test_plan_frontmatter_status_done(self):
        """plan-hr-cost-mvp-260625.md frontmatter status == done after v1 rehome."""
        plan_path = (
            VAULT_ROOT
            / "10_RAW" / "projects" / "v1-dashboard"
            / "plans" / "plan-hr-cost-mvp-260625.md"
        )
        assert plan_path.exists(), f"파일 없음: {plan_path}"
        content = plan_path.read_text(encoding="utf-8")
        fm = db.parse_frontmatter(content)
        assert fm.get("status", "").strip() == "done", (
            f"status가 done이 아님: {fm.get('status')}"
        )

    def test_plan_not_in_active_scan(self):
        """scan_active_plans() 결과에 done plan이 없음."""
        active = db.scan_active_plans()
        stems = [f.path.stem for f in active]
        assert "plan-hr-cost-mvp-260625" not in stems, (
            "status=done인 plan이 active_plans에 포함되어 있음"
        )


# ---------------------------------------------------------------------------
# US-006: R.S.md §7.5 존재 검증
# ---------------------------------------------------------------------------

class TestRSmd75:

    RS_PATH = Path(r"C:\Users\Pulmuone\.claude\commands\R.S.md")

    def test_section_header_exists(self):
        """R.S.md에 §7.5 섹션 헤더 존재."""
        assert self.RS_PATH.exists(), f"R.S.md 없음: {self.RS_PATH}"
        content = self.RS_PATH.read_text(encoding="utf-8")
        assert "### 7.5. 대응 Plan status 전환 제안" in content

    def test_section_between_7_and_8(self):
        """§7.5가 §7(Light /projects)과 §8(Light /ingest) 사이에 위치."""
        content = self.RS_PATH.read_text(encoding="utf-8")
        idx_7 = content.find("### 7. Light /projects")
        idx_75 = content.find("### 7.5.")
        idx_8 = content.find("### 8. Light /ingest")
        assert idx_7 < idx_75 < idx_8, (
            f"순서 오류: §7={idx_7}, §7.5={idx_75}, §8={idx_8}"
        )

    def test_section_content_keywords(self):
        """§7.5 내용에 핵심 키워드(best-effort, AskUserQuestion, status-change) 포함."""
        content = self.RS_PATH.read_text(encoding="utf-8")
        # §7.5 섹션만 추출
        start = content.find("### 7.5.")
        end = content.find("### 8.", start)
        section = content[start:end]
        for kw in ["best-effort", "AskUserQuestion", "status-change", "매칭 순서"]:
            assert kw in section, f"§7.5에 '{kw}' 없음"


# ---------------------------------------------------------------------------
# US-007: WIKI-01/02 stage graph lint
# ---------------------------------------------------------------------------

class TestWikiStageLint:

    def _make_stage_vault(self, tmp_path: Path) -> tuple[Path, Path]:
        wiki = tmp_path / "20_WIKI"
        projects = wiki / "projects" / "demo"
        raw = tmp_path / "10_RAW" / "projects" / "demo" / "results"
        projects.mkdir(parents=True)
        raw.mkdir(parents=True)
        (raw / "result-ok-260731.md").write_text("---\ntype: result\n---\n", encoding="utf-8")
        (projects / "demo.md").write_text(
            "---\ntype: project-index\nproject: demo\nstage_enabled: true\ncurrent_stage: 0\n---\n",
            encoding="utf-8",
        )
        return wiki, tmp_path / "10_RAW" / "projects"

    def test_wiki01_reports_missing_target(self, tmp_path: Path):
        wiki, raw_root = self._make_stage_vault(tmp_path)
        page = wiki / "projects" / "demo" / "synthesis.md"
        page.write_text("[[result-ok-260731]] [[result-missing-260731]]\n", encoding="utf-8")

        broken = db.check_wiki_broken_links(wiki, tmp_path)

        assert [(item[1], item[2]) for item in broken] == [(1, "result-missing-260731")]

    def test_wiki02_reports_unassigned_raw_target(self, tmp_path: Path):
        wiki, raw_root = self._make_stage_vault(tmp_path)
        projects = wiki / "projects" / "demo"
        (projects / "synthesis.md").write_text("[[result-ok-260731]]\n", encoding="utf-8")
        (projects / "stage-0-demo.md").write_text(
            "---\ntype: project-stage\nproject: demo\n---\n", encoding="utf-8"
        )

        findings = db.check_stage_assignments(wiki / "projects", raw_root)

        assert findings == [("demo", "result-ok-260731")]

