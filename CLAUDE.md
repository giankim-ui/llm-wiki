# Vault CLAUDE.md (LLM-Wiki Schema v2.2)

This vault is an LLM-maintained dual-axis knowledge base. You are the maintainer.

## Folder ↔ Layer Mapping (BINDING)
- `10_*`, `90_*`, `_attachments/`  → Layer 1 (Raw). NEVER modify.
- `20_*`, root `INDEX.md`/`LOG.md`/`MAP.md`  → Layer 2 (Wiki). LLM writes only. .md only.
- `/CLAUDE.md`, `_templates/`  → Layer 3 (Schema).

## Two Axes
- **Asset axis**: `10_RAW/assets/<CATEGORY>-<ID>/`, `20_WIKI/assets/<ID>/`
- **Project axis**: `10_RAW/projects/<slug>/`, `20_WIKI/projects/<slug>/`
- Shared: `20_WIKI/{concepts,themes,comparisons,industry,macro,frameworks,methodology,screening,entities,decisions}/`

## 3-Tier Navigation
- Tier 1: `/INDEX.md` — **볼트 전체 카탈로그** (2026-08-03 개정, second-brain 편입). 대시보드가 아니라 `20_WIKI/` 전 페이지를 폴더별로 나열·재생성한다. `<!-- @generated -->` 구간만 자동 갱신, `<!-- @user -->` 구간은 절대 침범 금지. `/LOG.md` cross-axis recent
- Tier 2: `20_WIKI/{projects,assets,entities,decisions}/{axis}-INDEX.md` + `{axis}-LOG.md` (entities·decisions 는 LOG 없음, 이벤트는 root `LOG.md`)
- Tier 3: `20_WIKI/{projects,assets}/<item>/<item>.md`  ← folder-note: 파일명 = 폴더명
- Shared INDEX: `20_WIKI/{concepts,themes,comparisons,methodology,entities,decisions}/<folder>-INDEX.md` — axis 무관 공유 폴더 INDEX. 별도 LOG 없이 이벤트는 root `LOG.md`에 기록.

## Rules
1. NEVER modify Layer 1 raw. (단, `10_RAW/`에 새 파일을 이관·생성하는 것은 허용 — 기존 파일 편집만 금지)
2. ALWAYS read root `INDEX.md` for navigation queries; `{axis}-INDEX.md` for axis-scoped queries.
<span style="color:red">4. ALWAYS append to LOG.md (axis-appropriate) after **every** plan/result/handoff Write AND after ingest/query/lint. **Format (통일 — 표 형식, 파일별 1행)** (per-file 정책 반영):
- 날짜 헤더 `## YYYY-MM-DD` + 표 헤더(`| 시간 | 이벤트 | 파일 | 1줄 요약 |` + `|---|---|---|---|`) 삽입 후 첫 행 추가.
- 같은 날이면 기존 표에 행만 추가: `| HH:MM | <event> | [[파일명]] | <요약≤60자> |`
- **처리된 .md 파일 1건당 표 1행** — batch 요약("N건 갱신", "X건 + Y건") 금지.
- **시간 = 파일 최초 생성 시각(ctime)** — 최종 수정 시각(mtime) 사용 금지 (vault open으로 갱신됨).
- **표 행은 시간 오름차순 정렬** (HH:MM 기준, 같은 날 내에서).
- 시분(HH:MM) 필수 — plan-version 포함 모든 이벤트.
- 세부 bullet-point 확장 금지 — 표 행 1줄로 완결.
- synthesis.md Δ 줄 ≈ LOG 표 행 1줄 요약 = 동일 granularity.
**ingest 후에는 DAILY.md와 INDEX.md를 갱신한다** — `python scripts/daily_brief.py` (인자 없음) 실행. `--skip-if-today` 사용 금지.</span>
5. ALWAYS ensure frontmatter on every .md.
6. NEVER skip cross-reference: ingest must touch INDEX.md(s) + LOG.md + ≥1 entity/concept/theme/comparison page besides item folder.
7. NEVER duplicate analysis/document content in wiki. synthesis.md = compounding log only (5~10 lines per item, Δ vs prior). **이 규칙은 재작성 금지 조항이 아니다** — 명확화(2026-08-03, second-brain 편입): 등급별 쓰기 범위는 `## Writing Scope by Tier (BINDING)` 참조.
8. YAML `tags` MUST use block sequence format (never inline array). Empty = `tags:` (no value). Tags MUST NOT start with a number — prefix codes with a descriptive type prefix (e.g. `type-001` not `001`).
   ```yaml
   # CORRECT
   tags:
     - knowledge-base
     - type-001
   # WRONG — causes Obsidian "유형이 일치하지 않습니다. 태그가 예상됩니다" error
   tags: [knowledge-base, 001]
   ```
9. INGEST ORDER (BINDING): `20_WIKI/` 페이지 생성 전, 소스 raw 파일이 반드시 `10_RAW/` 에 먼저 존재해야 한다. `mirrors_raw` 가 `10_RAW/` 외부를 가리키면 INVALID — wiki 생성 전 raw 이관을 먼저 완료하라.

## Writing Scope by Tier (BINDING, 2026-08-03 신설)

second-brain 스킬 편입(`reconcile`·`synthesize`·`/ingest` 재작성)으로 "오래된 사실을 교체"하는 쓰기가 처음 도입된다. Rule 7 은 재작성 금지 조항이 아니라 "내용 복제 금지 + `synthesis.md` 는 누적 로그" 규정이었다 — 과거 조사 문서가 이를 append-only 로 과잉 해석했다. 등급별 쓰기 범위를 아래로 명문화한다.

| 등급 | 대상 | 규칙 |
|---|---|---|
| **갱신 (재작성 허용)** | folder-note(hub), stage note, concept, entity, `20_WIKI/decisions/*`, `20_WIKI/projects/*/decisions.md` | 오래된 사실을 교체한다. 단 `## History` 섹션으로 이전 주장·출처·날짜를 남긴다. entity 는 `timeline:` 행 추가로 대체 |
| **덧붙이기만** | `synthesis.md`, `LOG.md`, `{axis}-LOG.md` | 표 행 추가만. 과거 행 내용 수정 금지 (링크 표기 정정은 예외, 사용자 승인 필요) |
| **구간 재생성** | `INDEX.md`, `{axis}-INDEX.md` | `<!-- @generated -->` 안쪽만. `<!-- @user -->` 구간 침범 절대 금지 |
| **읽기 전용** | `10_RAW/` 기존 파일, `_attachments/`, `90_ARCHIVE/` | Rule 1. 신규 파일 생성만 허용 |

entity 페이지는 개인정보 경계를 지킨다 — 업무 관계자 수준(담당 조직·벤더·도구)만 기록하고, 직원 개인의 사번·평가·급여는 절대 넣지 않는다.

## Authority Hierarchy (BINDING, 2026-08-03 신설)

`reconcile` 이 모순을 판정할 때, 또는 두 문서의 사실이 어긋날 때 아래 순서로 어느 쪽이 참인지 정한다.

| 등급 | 근거 | 예 |
|---|---|---|
| 1 | 사용자 확정 | 대화에서 confirm 한 것. `status` 변경은 이미 사용자 confirm 필수 |
| 2 | 실측·검증 출력 | lint 결과, pytest, DB 쿼리, 파일 수 카운트 |
| 3 | `result-*` 문서 | 빌드 통과 + 체크리스트가 붙은 완료 기록 |
| 4 | `20_WIKI/decisions/*` · `decisions.md` · gotchas | 사람이 판정을 끝낸 사후 기록 |
| 5 | `synthesis.md` · `LOG.md` | 시간순 관찰. 당시엔 사실이나 갱신되지 않음 |
| 6 | `plan-*` · `research` · clipping | 의도·조사. 아직 검증 안 됨 |

- 동급끼리 부딪히면 **날짜 최신** 우선
- entity 는 `timeline:` 의 `from`/`until` 이 등급 판정보다 우선 — 시점이 명시된 사실은 그 시점에서 참
- `CLAUDE.md`·`_templates/` 는 사실이 아니라 구조 규정이므로 서열 밖에 두고 항상 우선
- `~/.claude/memory/` 는 볼트 밖이고 "Claude 가 일하는 방식" 이라 모순 판정 대상이 아니다 — `reconcile` 스캔 제외

## Raw Reading Discipline (MOS Lesson — BINDING)
1. NEVER Read .json/.html/.md in `10_RAW/` in full. Coordinates first.
2. Coordinates = (item, version/date, section/Item).
3. If unknown, consult `20_WIKI/concepts/sources/...-structure.md`.
4. If still unclear, ASK user. Free-exploration full-read FORBIDDEN.
5. Each ingest's LOG entry must record raw read coordinates or "none".

## Mirror Principle
1. Information for Obsidian graph/search/Dataview must exist as .md in `20_WIKI/`.
2. Raw .jsx/.html/.json/.md stays in `10_RAW/`.
3. Wiki .md derived from raw must include `mirrors_raw: "[[<filename>]]"` frontmatter — file wikilink only, NEVER folder link (folder link causes Obsidian to create stray .md).
4. ALL raw file references in wiki .md (tables, lists, body text) must use `[[filename]]` wikilink — NEVER backtick path strings. Backtick renders as unclickable code text and breaks Obsidian graph edges.
5. Lint check: `mirrors_raw` 링크가 `10_RAW/` 내 실제 파일을 가리키는지 월 1회 검증. `10_RAW/` 외부 경로 참조는 raw 이관 미완료로 판정 → 즉시 수정.

## Status Vocabulary (BINDING)
- Project: `active | blocked | paused | done | archived`
- Asset: `watchlist | holding | archived`
- Concept/Theme/Comparison/Framework: `draft | stable`
- Plan (raw): `active | done`
- `status` change requires user confirm; LLM proposes only.

## LOG Event Vocabulary (BINDING)
decision, plan-version, result, phase-start, phase-complete, status-change, concept-extracted, theme-extracted, handoff, query, lint, clipping, research, reconcile, synthesize

`reconcile`·`synthesize` 는 2026-08-03 second-brain 편입으로 추가 (13개 → 15개). `decision`·`concept-extracted` 로 뭉개지 않는다 — 어휘를 뭉개면 나중에 탐지 불가한 사례가 LOG-02 로 이미 있었다.

**`ingest`는 워크플로우 이름이며 LOG/synthesis 이벤트 값으로 절대 사용 금지.** `| ingest |` 쓰기는 PreToolUse 훅(`event-vocab-guard.py`)이 차단한다. `/projects` 이관은 LOG/synthesis 미기록 — `/ingest` 단계에서 파일별 기록.

## Workflows
- Reading Discipline: see PLAN v2.2.x §6.0 ("C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\10_RAW\projects\knowledge-management\plans\PLAN_통합지식관리체계_v2.2.1_260505.md")
- Ingest: §6.1 → `/ingest` 커맨드
- Query: §6.2 → `/query` 커맨드. **file-back 경로 = `20_WIKI/methodology/<주제>-<YYMMDD>.md`** (BINDING — PLAN v2.0.0의 `50_RESEARCH/` 는 폐기 경로). 가치 있는 발견은 반드시 wiki 회수, `query` 이벤트로 root LOG 기록 (project/asset scope는 해당 axis LOG에도 동일 이벤트 기록, BINDING).
- Lint: §6.3
- Weekly pipeline (`reconcile → synthesize → finalize → audit`, `scripts/weekly_gate.py`): **자동 진행 (BINDING, 2026-09-07 신설)**. 한 단계 완료(result JSON 기록) 후 다음 단계·lint auto-fix 진행 여부를 사용자에게 묻지 않고 끝까지 실행한다. `AskUserQuestion`은 치명적·비가역적 이슈(돌이킬 수 없는 쓰기, 실질 개인정보 노출, 근거 없는 authority-tie)에만 사용 — 통상적 단계 전환은 해당하지 않는다.

## Agent Dispatch Policy (BINDING)
아래 **규칙 기반 작업**은 반드시 `Agent` tool (model: `haiku`)로 병렬 처리한다.
독립적인 작업이 2개 이상이면 반드시 단일 메시지에서 동시에 Agent 호출한다.

**Agent(Haiku) 대상 — 규칙 기반:**
- 템플릿 기반 wiki 페이지 생성 (asset/project/concept bootstrap, synthesis stub 포함)
- INDEX.md / LOG.md 업데이트 (행 추가·수정)
- wikilink 수정·교체 (다수 파일)
- raw 파일 이관 (외부 → `10_RAW/`)
- Lint 검사

**직접 수행(Sonnet) 대상 — 판단 필요:**
- synthesis compounding Δ 추가 (raw 읽고 내용 판단 필요한 경우)
- Query 분석·응답
- Comparison 작성
- Schema·CLAUDE.md 변경

## Frontmatter type Vocabulary
asset-index, asset-synthesis, project-index, project-synthesis, project-stage, concept, theme, comparison, framework, plan, research, chat-extract, source-structure, handoff, log, index, bottleneck, entity, decision-record, conflict

`entity`·`decision-record`·`conflict` 는 2026-08-03 second-brain 편입으로 추가 (16개 → 19개). 선택 키(옵션): `auto_generated`(bool), `entity_kind`(person|company|tool), `timeline`(array), `description`(string, 카탈로그 한 줄 설명 출처).

## Gotchas

### LOG-01 | LOG 날짜 헤더는 ctime 날짜 기준 (로그 작성일 아님)
**현상**: `result-distrib-save-260528` (ctime 5/28)이 6/1에 로깅되면서 `## 2026-06-01` 아래 잘못 배치됨.  
**원인**: Rule 4가 `## YYYY-MM-DD` 날짜 기준을 명시하지 않아 구현 시 "오늘"을 사용.  
**규칙**: LOG 행 추가 시 `## YYYY-MM-DD` 헤더는 **파일 ctime의 날짜**를 사용한다. 오늘 세션에서 로깅하더라도 ctime이 다른 날이면 해당 날짜 섹션에 삽입(없으면 생성)한다.  
**판별법**: 파일명 `YYMMDD`가 오늘과 다르면 ctime 확인 후 해당 날짜 섹션에 배치.

### LOG-02 | LOG/synthesis 이벤트에 금지 어휘(`ingest` 등) 사용 금지
**현상**: `/projects` 실행 후 LOG에 `| ingest |` 이벤트가 3번 반복 기록됨.  
**원인**: `/projects` 스킬 §5.7 템플릿이 `ingest` 이벤트를 사용하면서 `ingest.md` 금지 규칙과 충돌. `daily_brief.py`가 `ingest`를 유효 EventType으로 화이트리스트해 탐지 불가.  
**규칙**: LOG/synthesis 표 행 이벤트 컬럼에는 **BINDING 어휘 13개만** 허용. `ingest`를 쓰면 PreToolUse 훅(`event-vocab-guard.py`)이 쓰기를 즉시 차단. **`/projects`는 LOG/synthesis 미기록** — 파일별 LOG 기록은 `/ingest` 단계에서만.  
**감지**: `daily_brief.py` SessionStart에 LOG-02 금지 이벤트 전수 검사 포함.

### LINK-01 | 사용자 점검용 파일 링크는 볼트 기준 상대 링크
**현상**: Windows 절대경로 링크는 사용자가 Obsidian에서 바로 점검하기 어렵다.
**규칙**: 결과 보고·핸드오프의 로컬 파일 링크는 현재 볼트 루트 기준 상대 경로로 제공한다. 예: `[INDEX.md](INDEX.md)`, `[개념](20_WIKI/concepts/example.md)`.

### WIKI-03 | weekly-routine.cmd 반복 실패 시 자동 auto-fix 흐름 사용
**현상 (2026-09-07)**: `weekly-routine.cmd` 더블클릭 시 `wiki_lint.py`의 `ambiguous_targets`(8건)로 weekly gate 매번 차단. 수동 진단 결과 원인 3가지: (1) 신규 `.agents/` 폴더가 `_IGNORED_WALK_DIRS`에 없어 wikilink 후보로 스캔됨(`[[SKILL]]` 다중매치), (2) `daily_brief.py`의 WIKI-01 링크 해석기가 `10_RAW/` 하위 경로를 후보로 시도하지 않아 실제 존재하는 파일도 오탐(17건), (3) `[[HANDOFF-1]]`/`[[plan-dash-onprem-deploy-260806-v1.0]]` 같은 bare 링크가 여러 파일과 매치.
**원인**: `wiki_lint.py` walk 필터가 dot-prefixed 디렉터리를 일괄 무시하지 않았고, `daily_brief.py` 링크 해석기의 후보 루트 목록이 `10_RAW/`를 빠뜨렸으며, 일부 표 행이 전체경로 대신 bare 파일명으로 링크돼 있었음.
**규칙**: `scripts/wiki_lint.py`(dot-dir 전체 제외)와 `scripts/daily_brief.py`(`10_RAW/` 후보 추가)를 수정해 재발 원인을 제거함(커밋 `198aeda`). 그래도 새로운 lint 차단이 재발하면 `scripts/weekly_gate.py`가 `_auto_fix_lint()`로 **주 1회 한도**의 자동 수정을 시도한다 — lint 차단 시 `claude -p` 서브프로세스를 1회 스폰해 진단·수정 후 재검증하고, 결과를 `.vault-meta/weekly/lint-autofix-issue-{week}.md`에 기록한다. 이미 해당 주에 시도했다면(마커: `%TEMP%/claude-weekly-state/autofix-attempted-{week}.json`) 재시도하지 않고 이슈 리포트 경로만 안내 — 무한 루프 방지. 강제 재시도는 `weekly_gate.py --force`.
**감지**: `.vault-meta/weekly/lint-autofix-issue-*.md` 존재 여부로 자동 수정 이력 확인. `resolved: no`면 수동 `/debug` 필요.
