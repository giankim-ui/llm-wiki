# Vault CLAUDE.md (LLM-Wiki Schema v2.2)

This vault is an LLM-maintained dual-axis knowledge base. You are the maintainer.

## Folder ↔ Layer Mapping (BINDING)
- `10_*`, `90_*`, `_attachments/`  → Layer 1 (Raw). NEVER modify.
- `20_*`, root `INDEX.md`/`LOG.md`/`MAP.md`  → Layer 2 (Wiki). LLM writes only. .md only.
- `/CLAUDE.md`, `_templates/`  → Layer 3 (Schema).

## Two Axes
- **Asset axis**: `10_RAW/assets/<CATEGORY>-<ID>/`, `20_WIKI/assets/<ID>/`
- **Project axis**: `10_RAW/projects/<slug>/`, `20_WIKI/projects/<slug>/`
- Shared: `20_WIKI/{concepts,themes,comparisons,industry,macro,frameworks,methodology,screening}/`

## 3-Tier Navigation
- Tier 1: `/INDEX.md` dashboard, `/LOG.md` cross-axis recent
- Tier 2: `20_WIKI/{projects,assets}/{axis}-INDEX.md` + `{axis}-LOG.md`
- Tier 3: `20_WIKI/{projects,assets}/<item>/<item>.md`  ← folder-note: 파일명 = 폴더명

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
**ingest 후에는 DAILY.md도 갱신한다** — `python scripts/daily_brief.py` (인자 없음) 실행. `--skip-if-today` 사용 금지.</span>
5. ALWAYS ensure frontmatter on every .md.
6. NEVER skip cross-reference: ingest must touch INDEX.md(s) + LOG.md + ≥1 entity/concept/theme/comparison page besides item folder.
7. NEVER duplicate analysis/document content in wiki. synthesis.md = compounding log only (5~10 lines per item, Δ vs prior).
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
decision, plan-version, result, phase-start, phase-complete, status-change, concept-extracted, theme-extracted, handoff, ingest, query, lint

## Workflows
- Reading Discipline: see PLAN v2.2.x §6.0 ("C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\10_RAW\projects\knowledge-management\plans\PLAN_통합지식관리체계_v2.2.1_260505.md")
- Ingest: §6.1
- Query: §6.2
- Lint: §6.3

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
asset-index, asset-synthesis, project-index, project-synthesis, concept, theme, comparison, framework, plan, research, chat-extract, source-structure, handoff, log, index, bottleneck
