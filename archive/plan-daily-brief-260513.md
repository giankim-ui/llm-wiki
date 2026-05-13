---
type: plan
status: active
project: knowledge-management
created: 2026-05-13
tags:
  - daily-brief
  - logging
  - automation
---

# Plan: 출근 브리핑 시스템 (DAILY.md + LOG.md 보강 + 자동화)

> <span style="color:red">**📝 현재 라운드 = 1 — 2026-05-13 사용자 코멘트 2건 반영본**: ① "오늘 미완 plan" 표에도 시간 컬럼 추가, ② P.S/R.S 슬래시 명령에 frontmatter 강제 룰 확인 결과 반영 (없음 → 별도 STEP 추가).</span>

작성일: 2026-05-13
대상: 출근 시 "어제 무슨 일을 했고 / 오늘 무엇을 해야 하는지" 1 페이지로 한눈에 파악
연관: vault `LOG.md`, `INDEX.md`, CLAUDE.md §4 (LOG append 룰)

---

## 1. 문제 정의

현재 LOG.md 한계:
1. **이벤트 누락** — 어제(5/12) plan/result/handoff 12건 작성됐는데 LOG 에는 18:28 ingest 1줄만. CLAUDE.md 규칙 4 위반 사례 누적.
2. **시간 정보 부재** — `plan-version` 포맷이 "날짜만" 이라 흐름(오전→오후→야간) 추적 불가.
3. **요약 없음** — 파일명만으로 "무엇·왜" 미파악.
4. **"오늘 할 일" 칸 없음** — LOG 는 과거 기록 전용. 미완 plan(`status:active`) 집계 위치 없음.

목표: vault 루트에 `DAILY.md` 신설 + LOG.md 보강 + 자동화 (SessionStart hook + 수동 명령어).

---

## 2. 사용자 결정 사항 (확정)

| 항목 | 결정 |
|---|---|
| 메인 브리핑 위치 | **DAILY.md 신설 + LOG.md 보강** (INDEX.md 는 현행 유지) |
| Backfill 범위 | 어제(5/12) 분만 — 5/11 이전은 그대로 |
| 자동화 방식 | SessionStart hook + 수동 명령어 둘 다 |
| 표시 위치 추가 메모 | "로그 보강도 같이 진행" (LOG.md 룰 강화 동시 진행) |

---

## 3. 산출물 3종

<span style="color:red">### 3.1 `DAILY.md` (vault 루트) — 매일 첫 세션 시 자동 갱신 (코멘트 ① 반영: 미완 plan 표에 시간 컬럼)</span>

> 💬 **사용자 원본 코멘트 1**: "여기도 위와 같이 시간이 있어야돼!"

**구조 (mock-up)**:

```markdown
---
type: daily-brief
updated: 2026-05-13 09:15
scope: root
---

# Daily Brief — 2026-05-13 (Wed)

## 한 줄 요약
- **어제 흐름**: HCROI 재설계 → backdata plan 3건 → HCROI OFS 완성(✅) → HC 스키마 P1-a → 지원조직+퇴사율 P1-b (마지막 plan = `plan-spt-tur-260512`)
- **오늘 시작점**: P1-b DDL/schema.yaml 증분 구현 대기 (`plan-spt-tur-260512` 사용자 검토 완료 시)

## 어제 (2026-05-12)
| 시간 | 이벤트 | 파일 | 1줄 요약 |
|---|---|---|---|
| 09:01 | plan-version | [[plan_duckdb_summary-260511]] | DuckDB 요약 plan |
| 09:58 | plan-version | [[plan-hcroiRe-260512-v2.0.0]] | HCROI 재설계 v2 |
| 10:16 | plan-version | [[plan-hcroi-bu-csv-260512]] | BU CSV 매핑 |
| 10:36 | plan-version | [[plan-backdata-salaries-260512]] | 인건비 backdata |
| 11:07 | plan-version | [[plan-backdata-hc-260512]] | HC backdata |
| 11:27 | handoff | [[handoff-schema-260511]] | 스키마 handoff |
| 14:28 | plan-version | [[plan-hcroi-ofs-260512]] | HCROI OFS plan |
| 15:49 | result | [[result-hcroi-ofs-260512]] | ✅ HCROI OFS 빌드 통과 |
| 16:03 | plan-version | [[plan-hc-schema-260512]] | HC 스키마 P1-a |
| 16:26 | handoff | [[HANDOFF-1__HR-indexData]] | 전체 handoff |
| 18:11 | plan-version | [[plan-spt-tur-260512]] | 지원조직+퇴사율 P1-b ← **마지막 plan** |
| 18:16 | result | [[result-hcroi-aud-fix-260512]] | ✅ HCROI 감사 fix |
| 18:20 | result | [[result-hr-pipeline-260512]] | ✅ HR 파이프라인 |

## 오늘 (2026-05-13) — 미완 plan (status:active)
| 마지막 활동 | Plan | Project | 다음 작업 |
|---|---|---|---|
| 어제 18:11 | [[plan-spt-tur-260512]] | anlyz-hrIndexData | DDL/schema.yaml 증분 구현 대기 |
| 어제 16:03 | [[plan-hc-schema-260512]] | anlyz-hrIndexData | P1-a 선행 (위 plan 의존) |
| 어제 11:07 | [[plan-backdata-hc-260512]] | anlyz-hrIndexData | backdata 적재 |
| 어제 10:36 | [[plan-backdata-salaries-260512]] | anlyz-hrIndexData | 인건비 backdata 적재 |

# "마지막 활동" 컬럼 = plan 파일 mtime 의 상대 표기. 오늘이면 "오늘 HH:MM", 어제면 "어제 HH:MM", 그 이전이면 "MM-DD HH:MM".

## 진행 중 프로젝트
| Project | Phase | Last Activity |
|---|---|---|
| [[anlyz-hrIndexData]] | phase1-pipeline | 2026-05-12 18:20 |
| [[okr-matrix]] | v2.2-ops | 2026-05-11 |
| [[meeting-db]] | operations | 2026-05-11 |
```

**규칙**:
- 매일 첫 세션 시 hook 이 덮어쓰기 (어제 = now-1day 기준)
- 같은 날 여러 번 호출돼도 idempotent (mtime 기준 재계산)
- `updated` frontmatter 갱신 시각 박힘

---

### 3.2 `LOG.md` 보강 — 누락 backfill + 향후 룰 강화

**현행 LOG.md (5/12 분)**:
```
## [2026-05-12 18:28] ingest | /projects bulk raw migration (71 files → 6 slugs)
```

**보강 후 (어제 분만 backfill)**:
```markdown
## [2026-05-12] — anlyz-hrIndexData phase1-pipeline 집중 작업
- [09:01] plan-version | plan_duckdb_summary | DuckDB 요약 plan
- [09:58] plan-version | plan-hcroiRe-260512-v2.0.0 | HCROI 재설계 v2
- [10:16] plan-version | plan-hcroi-bu-csv-260512 | BU CSV 매핑
- [10:36] plan-version | plan-backdata-salaries-260512 | 인건비 backdata
- [11:07] plan-version | plan-backdata-hc-260512 | HC backdata
- [11:27] handoff | handoff-schema-260511 | 스키마 handoff
- [14:28] plan-version | plan-hcroi-ofs-260512 | HCROI OFS plan
- [15:49] result | result-hcroi-ofs-260512 | ✅ HCROI OFS 빌드 통과
- [16:03] plan-version | plan-hc-schema-260512 | HC 스키마 P1-a
- [16:26] handoff | HANDOFF-1__HR-indexData | 전체 handoff
- [18:11] plan-version | plan-spt-tur-260512 | 지원조직+퇴사율 P1-b
- [18:16] result | result-hcroi-aud-fix-260512 | ✅ HCROI 감사 fix
- [18:20] result | result-hr-pipeline-260512 | ✅ HR 파이프라인
- [18:28] ingest | /projects bulk raw migration (71 files → 6 slugs)
```

**규칙 변경 (CLAUDE.md §4 보강 사항 — 별도 patch 필요)**:
- 기존: `plan-version`은 `[YYYY-MM-DD]` 날짜만 / 실시간 이벤트는 `[YYYY-MM-DD HH:MM]`
- **변경**: 모든 이벤트 `[YYYY-MM-DD HH:MM]` 통일 + `| 1줄 요약(≤60자)` 부착
- LLM 이 plan/result/handoff `Write` 한 직후 LOG.md `Edit` 으로 1줄 append (CLAUDE.md 규칙 4 엄격 적용)

---

### 3.3 `scripts/daily_brief.py` + SessionStart hook

**위치**: `C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\scripts\daily_brief.py`

**동작**:
1. 인자 없이 호출 → vault 루트 자동 감지 (스크립트 위치 기준)
2. **수집 단계**: `10_RAW/projects/**/plans/*.md`, `**/results/*.md`, `**/handoffs/*.md`, `archive/**/*.md` 스캔, mtime 어제(0시~24시) 범위 필터
3. **분류 단계**: 파일명 prefix (`plan-`/`result-`/`handoff`) 또는 frontmatter `type` 으로 이벤트 분류
4. **요약 추출**: frontmatter `title` 또는 본문 `# ` 첫 줄에서 13~60자 요약
5. **DAILY.md 작성**: 위 §3.1 템플릿 채워서 vault 루트에 덮어쓰기
6. **LOG.md backfill (옵션 `--backfill-log` 플래그)**: 어제 분 누락 entries 만 LOG.md 에 시간순 append (이미 있는 시간 entry 는 skip)
7. **미완 plan 집계**: `10_RAW/projects/**/plans/*.md` 의 frontmatter `status: active` 추출 → DAILY.md "오늘 미완 plan" 표
8. **진행 중 프로젝트**: `20_WIKI/projects/projects-INDEX.md` 또는 `INDEX.md` 의 active project 리스트 재사용

**호출 경로 2가지**:

| 경로 | 트리거 | 빈도 |
|---|---|---|
| SessionStart hook | `.claude/settings.json` 의 `hooks.SessionStart` → `python scripts/daily_brief.py` | 매 세션 시작 시 |
| 수동 명령 | `/morning` 슬래시 명령 또는 `python scripts/daily_brief.py` 직접 실행 | 사용자가 임의로 |

**hook 등록 예시 (`.claude/settings.json` 추가 patch)**:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "python \"C:\\Users\\Pulmuone\\OneDrive - 풀무원\\20-Obsidian\\scripts\\daily_brief.py\""
      }
    ]
  }
}
```

**`/morning` 명령 등록**: `.claude/commands/morning.md` 신설 — 위 스크립트 실행 + DAILY.md 본문 콘솔 출력.

---

## 4. 실행 순서

1. **STEP 1**: `scripts/daily_brief.py` 작성 (Python 3.10+, frontmatter 파싱 `python-frontmatter` 또는 수동 regex)
2. **STEP 2**: 어제(5/12) 분 backfill 실행 → DAILY.md 생성 + LOG.md 보강
3. **STEP 3**: `.claude/settings.json` 에 SessionStart hook 추가
4. **STEP 4**: `.claude/commands/morning.md` 슬래시 명령 등록
5. **STEP 5**: 동작 검증 — 새 세션 시작해 DAILY.md 갱신 확인
6. **STEP 6**: vault CLAUDE.md §4 LOG 포맷 룰 patch (시간 통일 + 1줄 요약)
7. <span style="color:red">**STEP 6.5 (코멘트 ② 신설)**: `C:\Users\Pulmuone\.claude\commands\P.S.md` + `R.S.md` 패치 — 이동/저장 직후 대상 파일 frontmatter 부재 시 기본 블록 자동 삽입 (`type: plan`/`result`, `status: active`/`done`, `created: {today}`, `project: {slug}`). 신규 plan/result 100% frontmatter 보장 → DAILY.md `status:active` 집계 누락 0.</span>
8. **STEP 7**: result 파일 (`archive/result-daily-brief-260513.md`) 작성

---

<span style="color:red">## 5. 위험 / 미결 (코멘트 ② 반영: P.S/R.S frontmatter 룰 확인 결과 반영)</span>

> 💬 **사용자 원본 코멘트 2**: "내가 frontmatter 무조건 작성하게 /p.s, /r.s에 추가했던것 같은데 확인해줘"
>
> 📌 **확인 결과**: `C:\Users\Pulmuone\.claude\commands\P.S.md` 와 `R.S.md` 를 읽어 보았으나 **frontmatter 강제 작성 룰은 없음**. P.S 는 단순 `mv` 이동만 수행, R.S 의 result 템플릿도 `# Result: ...` 로 시작하고 frontmatter 블록 부재. → 본 plan 에 **별도 STEP 추가** 필요 (아래 §5 frontmatter 항목 + §4 STEP 6.5 참조).

| 위험 | 대응 |
|---|---|
| frontmatter 없는 raw plan 다수 — `status:active` 집계 누락 | (1) **P.S/R.S 슬래시 명령에 frontmatter 자동 삽입 룰 추가** (별도 STEP 6.5 신설) (2) 기존 plan 은 일괄 스캔 + frontmatter 없는 파일 콘솔 경고 → 사용자 일괄 추가 |
| OneDrive 동기화 중 파일 lock — Write 실패 | DAILY.md 쓰기 실패 시 retry 3회 (1초 간격) + 실패 시 콘솔 경고만 |
| SessionStart hook 매번 실행 → 같은 날 중복 갱신 | mtime 기준 idempotent, `updated` frontmatter 가 오늘 날짜면 skip 옵션 (`--skip-if-today`) |
| 어제 = 월요일이면 "어제" 가 금요일 데이터로 보여야 | 본 plan v1.0 에서는 단순 `now - 1day` 만 적용. 주말 처리는 별도 plan 으로 (필요 시 추후) |
| `10_RAW/projects/` 외부 plan (vault 루트 archive 등) 누락 | 스캔 경로에 `archive/` 도 포함. 단 vault 외부 (`!Claude` 등) 는 scope 밖 |

> 💬 **사용자 원본 코멘트 3 (위험표 인라인 4건 통합)**: ① OneDrive lock 대응 → "좋아", ② SessionStart hook 중복 갱신 → "좋아", ③ 월요일 = 금요일 보여야 → "맞음", ④ 외부 plan archive/ 포함 → "맞음". 모두 승인 — 표 셀 안 인라인 응답은 양식 깨짐 방지 위해 별도 줄로 이동 (CLAUDE.md "표 셀 내부 빨간색 마킹 금지" 룰 적용).

---

## 6. 비-목표

- INDEX.md 위젯화 (이번 plan 제외 — 사용자 결정)
- 5/11 이전 backfill (사용자 결정)
- 주말·휴일 처리 룰 (별도 plan)
- DAILY.md 의 long-form 회고 (이 plan 은 brief 만)

---

## 7. 진행 절차

1. 본 plan 사용자 재검토 → 코멘트 반영 후 v2.0 확정
2. `구현해줘` 명시 신호 받으면 STEP 1~7 순서대로 진행
3. 각 STEP 완료 후 사용자에게 짧게 보고
4. STEP 5 검증 통과 후 result 파일 작성
