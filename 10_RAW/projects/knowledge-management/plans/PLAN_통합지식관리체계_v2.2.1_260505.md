# PLAN — 통합 투자 지식 관리 체계 v2.2.1

- **작성일**: 2026-05-05
- **이전 버전**: v2.2.0 (260505), v2.1.0 (260505), v2.0.0 (260504), v1.0 (260504), 리스크격리 보완본 (260504)
- **반영 이론**: `llm-wiki.md` (LLM-as-wiki-maintainer 패턴)
- **대상 자산**: AI 채팅 기록 + JSX/HTML 분석 산출물(국가별) + plan*/result*/handoff* 운영 문서 + 캡처/스터디 자료
- **목표**: 흩어진 자료를 **"compounding 가능한 단일 지식 베이스"** 로 통합 — 사용자는 사고하고, LLM은 유지보수한다

> **v2.2.1 patch (vs v2.2.0)**:
> 1. 부록 A (루트 CLAUDE.md 골격) 외부 분리 → `REF_CLAUDE-md_skeleton_260505.md`
> 2. §12 즉시 실행 액션 — **Pilot-first** 권장으로 갱신
> 3. Phase 2 / Phase 3 — Pilot 변형 단계 명시 (한 번에 13h 일괄 구현 risk 감소)

---

## 0. v2.2.1 변경 요약

| 영역 | v2.2.0 | v2.2.1 |
|---|---|---|
| **부록 A** | 본문 내 ~80줄 CLAUDE.md 골격 통째 포함 | 본문 7-bullet 요약 + `REF_CLAUDE-md_skeleton_260505.md` 외부 분리. 향후 골격 갱신이 plan 수정과 분리 가능 |
| **즉시 실행 액션** | A/B/C 3안 (보수/중간/적극) — B안 13h 일괄 권장 | **Pilot-first** 권장. Phase 2/3 를 pilot(1+1개 자산·프로젝트, ~5h) → 검증 게이트 → full 확장으로 분할 |
| **Phase 2 / 3** | 일괄 5h + 5h | **2-pilot (1h) + 2-full (4h)**, **3-pilot (1h) + 3-full (4h)** 분리. 사고 시 단일 항목만 revert 가능 |
| **본문 길이** | ~700줄 | ~620줄 (부록 A 분리 효과) |

> v2.2.0 → v2.2.1 마이그레이션: v2.2.0 어떤 Phase도 시작되지 않았으므로 v2.2.1 Phase 0 부터 시작 가능.

> **v2.1.0 → v2.2.x 변경 요약은 v2.2.0 §0 참조**. 본 §0 은 v2.2.0 → v2.2.1 patch 만.

---

## 1. 이론적 토대

### 1.1 RAG vs Wiki — 결정적 차이

기존 NotebookLM/ChatGPT 업로드 방식은 **RAG**: 질문 시점에 원자료에서 청크를 검색 → 매번 처음부터 합성. **누적이 없다.**

LLM-Wiki는 다르다: LLM이 원자료를 한 번 읽으면 **wiki에 영구 통합**한다 — 엔티티 페이지를 갱신하고, 모순을 표시하고, 종합문을 갱신한다. **wiki는 점점 풍부해지는 compounding artifact**.

**우리 케이스에 대입**:
- Asset 측: `MSFT_분석대시보드.html`은 1회성 산출물 → 다음 분기에 인사이트 자동 누적 안 됨
- Project 측: `PLAN_통합지식관리체계_v2.2.1_260505.md` 결정 근거가 archive에 묻혀 다음 plan 작성 시 같은 함정 반복 가능
- 채팅 기록은 `claude.ai`에 갇혀 검색 불가 → 사고 흐름 휘발

→ 두 축 모두 **각 산출물이 wiki 페이지로 압축·연결되고, 새 산출물 추가 시 관련 페이지가 함께 갱신** 되어야 한다.

### 1.2 Wiki ≠ 분석/문서의 복제

llm-wiki.md 핵심:
> *"updating entity pages, revising topic summaries, noting where new data **contradicts** old claims, strengthening or challenging the **evolving synthesis**"*

**Wiki는 원본의 복제가 아니라 "테제(thesis)·방법론이 진화하는 곳"**.

| 축 | Wiki가 하지 말아야 할 것 | Wiki가 해야 할 것 |
|---|---|---|
| Asset | MSFT 분석을 wiki에 다시 쓰기 | 분석 1건 = 데이터 포인트 1개. compounding Δ 5~10줄 + concepts/themes/comparisons 갱신 |
| Project | plan 본문을 wiki에 다시 쓰기 | plan 1개 = 결정 set 1개. synthesis Δ + concept 추출(Mirror Principle 등) + decisions 누적 |

### 1.3 두 축 = 두 종류의 compounding

| 축 | Compounding 종류 | 사용자 가치 |
|---|---|---|
| **Asset** | Investment thesis | "이 종목 어떻게 봐야 하나" 누적 시각 |
| **Project** | Methodology | "어떻게 작업했더니 좋더라" 누적 패턴. 새 plan 작성 시 과거 결정 즉시 회수 |

→ 두 축은 **공유 concept** 으로 연결됨. 예: `cyclical-scoring` 은 multi-agent-stock-analysis 프로젝트 산출물이자 자산 분석 도구. 한 vault에서 양쪽이 데이터 포인트를 적립.

### 1.4 사용자와 LLM의 역할 분리

| 역할 | 사용자 | LLM (Claude Code) |
|---|---|---|
| 소스 큐레이션 | ★ | — |
| 좌표 통보 | ★ | — |
| 페이지 작성·갱신 | — | ★ |
| 종합·요약·교차참조 | — | ★ |
| INDEX/LOG/status 유지 | — | ★ |
| 깊이 사고·결정 | ★ | 보조 |
| **decisions.md 작성** (양 축 공통) | ★ | 참조만 |

---

## 2. 3계층 아키텍처 — 폴더 prefix가 곧 Layer

LLM-Wiki 원안의 3계층(Raw / Wiki / Schema)을 **물리적 폴더로 1:1 매핑**.

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: Schema   /CLAUDE.md  +  /_templates/                 │
└──────────────────────────────────────────────────────────────┘
            ↓ 규칙 정의
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: Wiki   /20_WIKI/  (LLM 단독, .md only)               │
│   ├ assets/<티커>/   (Asset axis)                             │
│   ├ projects/<프로젝트>/   (Project axis)                      │
│   ├ concepts/, themes/, comparisons/   (cross-axis 공유)      │
│   └ industry/, macro/, frameworks/, methodology/, screening/  │
└──────────────────────────────────────────────────────────────┘
            ↑ "이 시점 그 사실"의 immutable
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Raw   /10_RAW/  (immutable, 다양 포맷)               │
│   ├ assets/<티커>/   (.jsx/.html/.json/.md)                   │
│   ├ projects/<프로젝트>/   (.md plan/result/handoff)            │
│   ├ screening/, chats/, clippings/, docs/, attachments/, inbox/ │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 계층별 운영 원칙

**Layer 1 — Raw (`10_RAW/`)**:
- LLM 수정 금지. 영구 보존
- `S-anlyz*/!Report/` JSX/HTML도 raw (분석 파이프 결정적 산출물 = "이 시점 종목 사진")
- `PLAN_*.md`, `RESULT_*.md`, `HANDOFF*.md` 도 raw (그 시점 결정 = immutable)
- 채팅 raw export = gitignore
- **Raw Reading Discipline 적용** (§6.0)

**Layer 2 — Wiki (`20_WIKI/`)**:
- LLM 단독 작성·갱신. **.md only** (Obsidian 그래프·검색·Dataview 작동 단위)
- raw 비-md 파일의 핵심 정보는 LLM이 .md로 미러링 (Mirror Principle, §2.3)
- 사용자 메모는 `decisions.md` 또는 raw 의 `chats/`·`docs/` 에 분리
- 모든 페이지 frontmatter 필수 (§5)
- 모든 갱신 LOG.md 기록

**Layer 3 — Schema**:
- 볼트 루트 `CLAUDE.md` 신규 작성 (골격: `REF_CLAUDE-md_skeleton_260505.md` 참조)
- `S-anlyz*/CLAUDE.md`, `S-anlyz*/.claude/` **건드리지 않음**

### 2.2 폴더 prefix → 계층 식별 규칙

| Prefix | Layer | LLM 쓰기? | 파일 포맷 |
|---|---|---|---|
| `10_*` | 1 (Raw) | ❌ | 자유 |
| `20_*` | 2 (Wiki) | ✅ | .md only |
| `90_*` | 1 (Archive Raw) | ❌ | 자유 |
| `_attachments/` | 1 | ❌ | 이미지/PDF |
| `_templates/` | 3 | ✅ (스키마 변경 시) | .md |
| 루트 .md (CLAUDE/INDEX/LOG/MAP) | 2~3 | ✅ | .md |
| `S-anlyz*/` | 외부 도메인 | ❌ | — |

### 2.3 Mirror Principle (Obsidian 호환성)

**문제**: Obsidian 그래프·백링크·검색·Dataview 는 `.md` 위에서만 작동.

**해결**: raw 비-md 원본은 `10_RAW/` 보존, **LLM이 핵심 정보를 .md로 미러링** 해 `20_WIKI/` 에 둔다.

| Raw 파일 (Layer 1) | LLM이 만드는 미러 (Layer 2) |
|---|---|
| `10_RAW/assets/US-MSFT/reports/dashboard_260503.jsx` | `20_WIKI/assets/US-MSFT/synthesis.md` 의 compounding 항목 |
| `10_RAW/assets/US-MSFT/reports/SOURCE_PACKAGE_260503.json` | `20_WIKI/assets/US-MSFT/INDEX.md` Sources 표 |
| `10_RAW/projects/knowledge-management/plans/PLAN_v2.2.1_260505.md` | `20_WIKI/projects/knowledge-management/synthesis.md` 의 plan-version 항목 |
| `10_RAW/projects/knowledge-management/handoffs/HANDOFF-3.md` | 해당 프로젝트 INDEX의 handoff 표 + concept 추출 |
| `10_RAW/screening/20260503/US_스크리닝.html` | `20_WIKI/screening/260503_us-cyclical-themes.md` |
| `10_RAW/chats/claude/2026-04/raw.json` (gitignored) | `10_RAW/chats/claude/2026-04/_processed/<주제>.md` + 해당 종목/프로젝트 페이지 갱신 |

**원칙**: "Obsidian 그래프·검색에 들어가야 하는 정보는 LLM이 .md 미러를 만든다. 원본은 raw에 immutable artifact 로 둔다. 미러본에는 항상 원본 wikilink 포함."

---

## 3. 폴더 트리 (v2.2.x 정본)

```
!claudeProject/                          ← Obsidian 볼트 루트
│
├── CLAUDE.md                            ★ 볼트 스키마 (골격: REF_CLAUDE-md_skeleton_260505.md)
├── INDEX.md                             ★ Tier 1 dashboard (5초 진입)
├── LOG.md                               ★ Tier 1 cross-axis 최근 30일 highlight
├── MAP.md                               사람용 가이드
│
├── 10_RAW/                              ★ Layer 1 통째 — LLM 수정 금지
│   ├── assets/
│   │   └── <COUNTRY>-<TICKER>/
│   │       ├── reports/                 .jsx, .html, .json
│   │       ├── chats/                   .md
│   │       ├── clippings/               .md
│   │       └── docs/                    .md
│   ├── projects/
│   │   └── <project-slug>/
│   │       ├── plans/                   PLAN_*.md (immutable)
│   │       ├── results/                 RESULT_*.md
│   │       ├── handoffs/                HANDOFF*.md
│   │       ├── chats/                   .md
│   │       └── clippings/               .md
│   ├── screening/<YYYYMMDD>/
│   ├── chats/{claude,gemini}/<YYYY-MM>/raw.json (gitignored), _processed/
│   ├── clippings/, docs/, attachments/, inbox/
│
├── 20_WIKI/                             ★ Layer 2 통째 — LLM 단독, .md only
│   ├── assets/
│   │   ├── INDEX.md, LOG.md             ★ Tier 2 자산 카탈로그·시간선
│   │   └── <COUNTRY>-<TICKER>/
│   │       └── INDEX.md, synthesis.md, decisions.md
│   ├── projects/
│   │   ├── INDEX.md, LOG.md             ★ Tier 2 프로젝트 카탈로그·시간선
│   │   └── <project-slug>/
│   │       └── INDEX.md, synthesis.md, decisions.md
│   ├── concepts/
│   │   ├── INDEX.md                     reverse index (어느 concept이 어느 자산·프로젝트에서)
│   │   ├── pbr.md, economic-moat.md, cyclical-investing.md, fcf.md, ...
│   │   ├── llm-wiki-pattern.md, mirror-principle.md, raw-reading-discipline.md, ...
│   │   └── sources/
│   │       ├── us-sec-10k-structure.md, us-sec-10q-structure.md
│   │       ├── us-investing-transcript-structure.md
│   │       ├── kr-dart-yusil-structure.md, jp-edinet-yuho-structure.md
│   │       ├── source-package-schema.md
│   │       └── plan-document-structure.md
│   ├── themes/INDEX.md, ai-capex-burden.md, km-thesis-evolution.md, ...
│   ├── comparisons/INDEX.md, msft-vs-googl-cloud-margin.md, km-plans-v1-v2.0-v2.1-v2.2.md, ...
│   ├── industry/, macro/, frameworks/, methodology/, screening/
│
├── 90_ARCHIVE/handoffs/, lint-reports/
│
├── _templates/
│   ├── asset-INDEX.md, asset-synthesis.md
│   ├── project-INDEX.md, project-synthesis.md
│   ├── concept.md, theme.md, comparison.md
│   ├── source-structure.md, plan.md, chat-extract.md
│
├── S-anlyz/, S-anlyz-kr/, S-anlyz-jp/   (기존 유지 — Phase E에서만)
└── .obsidian/
```

### 3.1 v2.1.0 대비 폴더 변경점은 v2.2.0 §3.1 참조. v2.2.1 은 폴더 트리 변경 없음.

---

## 4. 3-tier Navigation 구조

### 4.0 사용자 pain → tier 매핑

| 사용자 질문 | 가는 곳 |
|---|---|
| "지금 살아있는 게 뭐? (5초)" | Tier 1 — 루트 INDEX.md |
| "최근 무슨 일?" (cross-axis) | Tier 1 — 루트 LOG.md |
| "active 프로젝트 다 보여줘" | Tier 2 — `20_WIKI/projects/INDEX.md` |
| "분석한 종목 다 보여줘" | Tier 2 — `20_WIKI/assets/INDEX.md` |
| "이 프로젝트 끝났나?" | Tier 2 또는 Tier 3 — `status` frontmatter |
| "비슷한 거 했나? (concept으로)" | Tier 2 — concepts INDEX 의 reverse index |
| "MSFT 마지막 분석 결정?" | Tier 3 — `20_WIKI/assets/US-MSFT/INDEX.md` |
| "이 프로젝트 결정 근거?" | Tier 3 — `20_WIKI/projects/<slug>/decisions.md` |

### 4.1 Tier 1 — 루트 INDEX.md (대시보드)

5초 진입용. 변경 빈도 높음 (LLM이 ingest 마다 갱신).

```markdown
---
type: index
scope: root
updated: 2026-05-05 22:00
maintained_by: claude-code
---

# Vault Dashboard
> Active projects: 3 / Watchlist assets: 12 / Last activity: 2h ago

## ★ Top of Mind

### Active Projects (3 most recent)
- [[20_WIKI/projects/knowledge-management/INDEX]] — v2.2.1 작성 / Phase 0 대기 · 2026-05-05
- [[20_WIKI/projects/multi-agent-stock-analysis/INDEX]] — 운영 안정 · 2026-05-03
- [[20_WIKI/projects/screening-mode/INDEX]] — 운영 안정 · 2026-04-28

### Recent Asset Activity (5 most recent)
- US-MSFT — analyzed 2026-05-03
- ...

## Deep Navigation
| 축 | INDEX | LOG |
|---|---|---|
| Projects | [[20_WIKI/projects/INDEX]] | [[20_WIKI/projects/LOG]] |
| Assets | [[20_WIKI/assets/INDEX]] | [[20_WIKI/assets/LOG]] |
| Concepts | [[20_WIKI/concepts/INDEX]] | — |
| Themes | [[20_WIKI/themes/INDEX]] | — |
| Comparisons | [[20_WIKI/comparisons/INDEX]] | — |

[[MAP|Vault Guide for Humans]]
```

### 4.2 Tier 1 — 루트 LOG.md

cross-axis 최근 30일 highlight only. 풀 history는 axis LOG에.

LLM 운영: ingest 시 highlight 여부 판단 (plan-version, phase-start/complete, status-change, 자산 분기 분석 = highlight).

### 4.3 Tier 2 — `20_WIKI/projects/INDEX.md` (★ pain 직접 해결)

```markdown
---
type: index
scope: projects
updated: 2026-05-05
---

# Projects Index

## ★ Active (최근 활동 30일 이내)
| Project | Status | Last Activity | Current Phase/Version | Blocker |

## Blocked / Waiting
## Paused
## Recently Done (지난 90일)
## Archived (90일+)

---

## ★ Concept Reverse Index
| Concept | Projects |
|---|---|
| [[../concepts/llm-wiki-pattern]] | knowledge-management |
| [[../concepts/mirror-principle]] | knowledge-management |
| [[../concepts/raw-reading-discipline]] | knowledge-management |
| [[../concepts/agent-orchestration]] | multi-agent-stock-analysis |
| [[../concepts/cyclical-scoring]] | multi-agent-stock-analysis, screening-mode |

## Theme Index
- [[../themes/km-thesis-evolution]]
- [[../themes/agent-architecture-evolution]]
```

### 4.4 Tier 2 — `20_WIKI/projects/LOG.md` (chronological)

**LOG event vocabulary (binding)**:

| Event | 의미 |
|---|---|
| `decision` | 설계 결정 |
| `plan-version` | 새 PLAN_*.md raw 추가 |
| `result` | RESULT_*.md raw 추가 |
| `phase-start` / `phase-complete` | phase 전환 |
| `status-change` | active ↔ blocked ↔ paused ↔ done |
| `concept-extracted` | 새 concept 페이지 도출 |
| `theme-extracted` | 새 theme 페이지 도출 |
| `handoff` | 세션 인계 |

### 4.5 Tier 2 — `20_WIKI/assets/INDEX.md`

Watchlist · Recently Analyzed · Holdings · All Assets · Theme Reverse Index · Sector Reverse Index 섹션. 자산 ingest 시 LLM이 갱신.

### 4.6 Tier 2 — `20_WIKI/assets/LOG.md`

자산 ingest/query/lint chronological. 분기 cadence라 noise 적음.

### 4.7 Tier 3 — 개별 프로젝트/자산 INDEX.md

자산은 v2.1과 동일. 프로젝트 신규 (`_templates/project-INDEX.md`).

---

## 5. Frontmatter 표준 + Status Vocabulary (binding)

### 5.1 공통 frontmatter

```yaml
---
type: asset-index | asset-synthesis | project-index | project-synthesis | concept | theme | comparison | framework | plan | research | chat-extract | source-structure | handoff | log | index
asset: US-MSFT                 # asset 관련 페이지만
project: knowledge-management  # project 관련 페이지만 (slug)
country: US | KR | JP | global
date: 2026-05-05
status: active | blocked | paused | done | archived | draft | stable    # §5.2
sector: tech | financial | energy | ...
tags: [...]
themes: [ai-capex, rate-cycle]
concepts: [moat, fcf, mirror-principle]
data_points: 4
source: claude-chat | gemini-chat | self | s-anlyz-pipeline | sec-filing | dart-filing | edinet-filing
related: ["[[20_WIKI/...]]"]
mirrors_raw: "[[10_RAW/...]]"   # 미러본 한정
last_lint: 2026-05-04
---
```

### 5.2 Status 어휘 — 항목별 binding

**Project (`type: project-index`)** — 5단계:

| Status | 정의 | 추가 frontmatter |
|---|---|---|
| `active` | 최근 30일 활동 / 진행 중 | `last_activity`, `current_phase`, `done_criteria` |
| `blocked` | 외부 의존 대기 | `blocker` (1줄) |
| `paused` | 사용자 의도적 중단 | `paused_since`, `resume_trigger` |
| `done` | 목표 달성 | `done_at`, `outcome` |
| `archived` | 90일 done 후 또는 폐기 | `archived_at` |

**Asset (`type: asset-index`)** — 3단계: `watchlist | holding | archived`

**기타**: concept/theme/comparison/framework `draft | stable`, plan `active | done`

### 5.3 Project 자동 갱신 규칙 (LLM 운영)

이벤트 발생 시 LLM 자동 갱신:
- 새 plan 작성 → `current_version`, `plan-version` LOG event
- phase 시작 → `current_phase`, `phase-start` LOG event
- 30일 활동 없음 → lint가 status 정합성 확인 제안

`status` 변경은 항상 사용자 confirm. LLM은 제안만.

### 5.4 Dataview 활용 (Phase 5)

```dataview
TABLE status, last_activity, current_phase, blocker
FROM "20_WIKI/projects"
WHERE type = "project-index" AND status = "active"
SORT last_activity DESC
```

---

## 6. 4대 오퍼레이션 — Reading Discipline / Ingest / Query / Lint

### 6.0 Raw Reading Discipline (모든 오퍼레이션 전제)

**원칙**: `10_RAW/` 의 .json/.html/.md 파일은 **좌표(연도 × Item/섹션) 없이 통째로 Read 하지 않는다**.

**Asset 축 좌표 어휘**:
- "MSFT FY2025 10-K Item 7 MD&A"
- "005380 2024 사업보고서 재무에 관한 사항"

**Project 축 좌표 어휘**:
- "PLAN v2.2.1 §6.0~§6.3 only"
- "PLAN v2.1.0 부록 A 만"
- "RESULT_<주제>_<날짜>.md 결론 섹션"

**좌표가 정해지는 경로**:
1. 사용자 직접 통보
2. 분석 파이프 결과 메시지 / plan 작성 시 사용자가 통보하는 Δ
3. wiki에 이미 distilled — `synthesis.md` 또는 `concepts/` 에서 충당

**좌표 모를 때**: `20_WIKI/concepts/sources/...-structure.md` 참조 → 후보 좌표 1~2개 결정 → 그래도 모르면 사용자에게 좌표 요청. 자유 탐색 raw read 절대 금지.

**위반 사례 (재발 금지)**: MOS 21년 10-K 통째 read → 컨텍스트 폭주.
- Plan 통째 read도 무시 못 함 — v2.2.x ~30KB, 5개 plan = 150KB
- supervisor 수집 상한(7/6/6)은 ingest 보호. 본 Discipline 은 query/synthesis 보호. 두 보호막 동시 작동

**lint에서 검출**: LOG.md raw read 좌표 기록 누락 시 lint 실패.

### 6.1 Ingest

**Trigger**: 사용자 "이 자료 흡수해줘" 또는 분석 파이프/사용자가 새 raw 파일 떨어뜨림.

**Workflow**:
1. raw 파일 안착 위치 확인 (assets/ vs projects/ vs chats/ ...)
2. 사용자/파이프로부터 좌표 + Δ 통보 받음
3. raw 통째 Read 금지. 좌표 부분만 핀포인트
4. 갱신 대상 페이지 결정 (n개 propagation):

   **Asset ingest**:
   - `20_WIKI/assets/<티커>/synthesis.md` compounding 항목 append
   - `20_WIKI/assets/<티커>/INDEX.md` Last Analyzed 갱신
   - `20_WIKI/assets/INDEX.md` Recently Analyzed 갱신
   - `20_WIKI/assets/LOG.md` append
   - 관련 `concepts/`, `themes/`, `comparisons/` 데이터 포인트
   - 루트 `INDEX.md`, `LOG.md` highlight 판단

   **Project ingest** (예: 새 plan-version):
   - `20_WIKI/projects/<slug>/synthesis.md` plan-version 항목 append
   - `20_WIKI/projects/<slug>/INDEX.md` `current_version`, `last_activity` 갱신
   - `20_WIKI/projects/INDEX.md` Active 표 갱신
   - `20_WIKI/projects/LOG.md` append
   - 도출 concept 있으면 `concepts/<new>.md` 신규 + `concepts/INDEX.md` reverse index
   - 루트 `INDEX.md`, `LOG.md`

5. 사용자에게 변경 페이지 목록 제시 → 확인 → 커밋

**예시: PLAN v2.2.1 자체 ingest** (이번 plan의 self-ingest):
```
입력: 10_RAW/projects/knowledge-management/plans/PLAN_v2.2.1_260505.md
좌표: §0 변경 요약만
Δ: Appendix A 분리, Pilot-first, Phase 2/3 pilot 분리
LLM raw read: 0회 (이미 작성한 내용)
영향:
  - 20_WIKI/projects/knowledge-management/synthesis.md  (plan-version 항목 append)
  - 20_WIKI/projects/knowledge-management/INDEX.md       (current_version: v2.2.1)
  - 20_WIKI/projects/INDEX.md, LOG.md
  - 20_WIKI/comparisons/km-plans-v1-v2.0-v2.1-v2.2.md   (v2.2.1 행 추가)
  - 루트 INDEX.md, LOG.md
```

### 6.2 Query

1. **Navigation 질문**:
   - "현재 active 프로젝트?" → `20_WIKI/projects/INDEX.md` 직진
   - "비슷한 거 했나?" → `20_WIKI/projects/INDEX.md` Concept Reverse Index 또는 `20_WIKI/concepts/<키워드>.md` cross-project 백링크
   - "MSFT?" → `20_WIKI/assets/US-MSFT/INDEX.md`
   - 일반 질문 → 루트 INDEX → drill-down
2. raw 필요 시 §6.0
3. 답변 + 출처 wikilink
4. 가치 있으면 wiki file-back (`20_WIKI/methodology/<주제>-<날짜>.md` 또는 `comparisons/`)

### 6.3 Lint (월 1회)

| 검사 | 도구 |
|---|---|
| **좌표 없는 raw read** | LOG.md grep — 발견 시 lint 실패 |
| **synthesis.md 비대화** | 항목당 평균 10줄 초과 → 복제 의심 |
| **status 정합성** | `active` 인데 `last_activity` 30일 초과 → 정정 제안 |
| **status: done 자동 archive 후보** | `done_at` 90일 초과 |
| **Concept reverse index 누락** | frontmatter `concepts:` 와 `concepts/INDEX.md` 일치 |
| 모순 / Stale / Orphan / 누락 concept / 깨진 링크 / Dead artifact | 표준 |

**산출물**: `20_WIKI/projects/LOG.md` + `20_WIKI/assets/LOG.md` lint 항목 + `90_ARCHIVE/lint-reports/<날짜>.md`.

---

## 7. 외부 채팅 Ingest 파이프라인

### 7.1 Claude.ai

1. 월 1회 Settings → Export data → JSON
2. `10_RAW/chats/claude/<YYYY-MM>/raw.json` (gitignored)
3. Claude Code 요청: 종목/프로젝트별 .md 분리, frontmatter `type: chat-extract, source: claude-chat, asset: <티커> | project: <slug>`
4. LLM이 `_processed/` 분리
5. 가치 있는 5~10개 → §6.1 Ingest → 종목 관련은 `10_RAW/assets/<티커>/chats/`, 프로젝트 관련은 `10_RAW/projects/<slug>/chats/`, 일반 연구는 `20_WIKI/methodology/`
6. raw.json gitignore. 가공 .md 만 커밋

### 7.2 Gemini

Google Takeout → 동일.

### 7.3 자동화 (Phase 5+)

PowerShell 폴더 감시 → 자동 skill 호출. v2.2 본문 외.

---

## 8. 리스크 격리 마이그레이션 (Phase 0~5, Pilot-first 분할)

> 비개발자 멘탈 모델: **"위험한 작업 = ① 커밋 ② 새 브랜치 ③ 푸시 + 태그"**.
> v2.2.1 의 핵심 변경: **Phase 2 / Phase 3 를 pilot + full 로 분리**. 사고 시 단일 자산·프로젝트만 revert 가능.

### Phase 0 — 안전망 (30분)

- 현재 master `git status` M 정리 (남길 건 커밋, 버릴 건 사용자 명시 확인)
- 태그 `git tag v-pre-kb-v2.2`
- 푸시 `git push origin master --tags`
- 새 브랜치 `git checkout -b kb-v2.2/phase1-skeleton`

### Phase 1 — 골격 + 스키마 (2.5시간)

- **브랜치**: `kb-v2.2/phase1-skeleton`
- 작업:
  - `10_RAW/{assets,projects,screening,chats,clippings,docs,attachments,inbox}/` 빈 폴더
  - `20_WIKI/{assets,projects,concepts,themes,comparisons,industry,macro,frameworks,methodology,screening}/` 빈 폴더 + 각 INDEX.md
  - `20_WIKI/concepts/sources/` 빈 폴더
  - `90_ARCHIVE/{handoffs,lint-reports}/`, `_templates/`
  - `_templates/` 9종 템플릿
  - **루트 `CLAUDE.md` 작성** — `REF_CLAUDE-md_skeleton_260505.md` 골격 복사 후 미세조정
  - 빈 루트 `INDEX.md`, `LOG.md`, `MAP.md`
  - `.gitignore` 보강
- 검증: Obsidian 볼트 열림, 폴더 진입, 템플릿 작동, CLAUDE.md 에 §6.0 + Mirror + Status Vocabulary 포함
- 머지 → `v-kb-v2.2-phase1`

### Phase 2-pilot — Asset 1 + Project 1 이관 (1시간) ★ v2.2.1 신규

- **브랜치**: `kb-v2.2/phase2-pilot`
- 목적: 폴더 prefix 매핑·git mv 패턴·검색 경험을 검증. **단일 자산·단일 프로젝트만**
- 작업:
  - **Asset 1개 (MSFT)**:
    - `S-anlyz/!Report/MSFT_분석대시보드.{jsx,html}` → `10_RAW/assets/US-MSFT/reports/dashboard_<날짜>.{jsx,html}`
    - `S-anlyz/raw/MSFT/SOURCE_PACKAGE.json` 복사
  - **Project 1개 (knowledge-management)**:
    - `archive/PLAN_통합지식관리체계_*.md` (v1.0/v2.0.0/v2.1.0/v2.2.0/v2.2.1) → `10_RAW/projects/knowledge-management/plans/`
    - `archive/PLAN_통합지식관리-리스크격리_*.md` → 동
    - `archive/REF_CLAUDE-md_skeleton_*.md` 그대로 (참고 raw)
    - `llm-wiki.md` → `10_RAW/projects/knowledge-management/clippings/llm-wiki_원본.md` (외부 출처 raw)
- 세이프티: `git mv`, 자산 1커밋 + 프로젝트 1커밋, 원본 폴더 보존
- 머지 → `v-kb-v2.2-phase2-pilot`

### Phase 3-pilot — 위 1+1개 Wiki 부트스트랩 (1시간) ★ v2.2.1 신규

- **브랜치**: `kb-v2.2/phase3-pilot`
- 작업:
  - **소스 스키마 가이드 1종 먼저**:
    - `20_WIKI/concepts/sources/plan-document-structure.md` (project pilot에 필요)
  - **Asset (US-MSFT) wiki**:
    - `20_WIKI/assets/US-MSFT/INDEX.md` (raw 메타 + SOURCE_PACKAGE URL 미러)
    - `20_WIKI/assets/US-MSFT/synthesis.md` stub 또는 5~10줄 Δ
    - `20_WIKI/assets/US-MSFT/decisions.md` 빈 파일
    - `20_WIKI/assets/INDEX.md` Watchlist 1행 + Theme reverse index 부트
    - `20_WIKI/assets/LOG.md` bootstrap 항목
  - **Project (knowledge-management) wiki**:
    - `20_WIKI/projects/knowledge-management/INDEX.md` (status, current_version 등 frontmatter 완비)
    - `20_WIKI/projects/knowledge-management/synthesis.md` — plan v1.0~v2.2.1 plan-version 항목 5~10줄씩
    - `20_WIKI/projects/knowledge-management/decisions.md` 빈 파일
    - `20_WIKI/projects/INDEX.md` Active 1행 + Concept Reverse Index 2~3건
    - `20_WIKI/projects/LOG.md` bootstrap (각 plan-version event)
  - **Concept stub 2~3개**:
    - `20_WIKI/concepts/llm-wiki-pattern.md`, `mirror-principle.md`, `raw-reading-discipline.md`
    - `20_WIKI/concepts/INDEX.md` reverse index 부트
  - **루트 채우기**:
    - 루트 `INDEX.md` dashboard (Active Projects 1 + Recent Asset 1)
    - 루트 `LOG.md` highlight 부트
- 머지 → `v-kb-v2.2-phase3-pilot`

### ★ Pilot 검증 게이트 (필수)

다음 모두 합격 시 Phase 2-full / 3-full 진행. 불합격 시 v2.3 plan 수정 후 재진행.

| 검증 항목 | 합격 기준 |
|---|---|
| Obsidian 볼트 정상 열림 | `.obsidian/` 인식, 폴더 트리 표시 |
| Asset Tier 3 작동 | `20_WIKI/assets/US-MSFT/INDEX.md` → `mirrors_raw` wikilink 클릭 → `10_RAW/.../dashboard_*.html` 외부 앱 오픈 |
| Project Tier 3 작동 | `20_WIKI/projects/knowledge-management/INDEX.md` → plans wikilink → raw `.md` 오픈 |
| Tier 2 navigation | `20_WIKI/projects/INDEX.md` Active 표에 km 1행, Concept Reverse Index 2~3건 표시 |
| Tier 1 dashboard | 루트 `INDEX.md` 5초 진입 가능, Active Projects 1행 + Recent Asset 1행 |
| Status frontmatter | km 프로젝트 INDEX 가 `status: active`, `current_version: v2.2.1` 표시 |
| Mirror Principle | wiki .md 의 `mirrors_raw:` 가 raw 와 1:1 매칭, 클릭 도달 |
| 분석/문서 복제 0건 | synthesis.md 항목당 5~10줄, plan 본문 통째 복사 없음 |
| LOG 좌표 기록 | `20_WIKI/projects/LOG.md` 의 plan-version 항목에 raw read 좌표 또는 "none" |

### Phase 2-full — 나머지 자산·프로젝트 이관 (4시간)

- **브랜치**: `kb-v2.2/phase2-full`
- Pilot 합격 후 진행. 작업:
  - 나머지 종목 raw 이관 (자산 1개당 1커밋)
  - 나머지 프로젝트 분류·이관 — `multi-agent-stock-analysis`, `screening-mode` (프로젝트 1개당 1커밋)
  - root `HANDOFF-*.md` 분류 (주 프로젝트 매핑 또는 `90_ARCHIVE/handoffs/`)
  - 스크리닝 raw → `10_RAW/screening/<YYYYMMDD>/`
  - 원본 폴더 (`S-anlyz/!Report/`, `archive/`) 보존
- 머지 → `v-kb-v2.2-phase2`

### Phase 3-full — 나머지 Wiki 부트 + 소스 가이드 6종 (4시간)

- **브랜치**: `kb-v2.2/phase3-full`
- 작업:
  - **소스 스키마 가이드 6종 추가**: us-sec-10k/10q/investing-transcript/source-package + kr-dart-yusil + jp-edinet-yuho
  - 나머지 Asset INDEX/synthesis/decisions 부트 + Tier 2 자산 INDEX/LOG 갱신
  - 나머지 Project (multi-agent, screening-mode) INDEX/synthesis/decisions 부트 + Tier 2 프로젝트 INDEX/LOG 갱신
  - 추가 concept stub 7~8개 (PBR/Cyclical/Moat/FCF/EPS quality + agent-orchestration/source-package-contract/...)
  - 추가 theme/comparison stub
  - 루트 INDEX/LOG full 부트
- 머지 → `v-kb-v2.2-phase3`

### Phase 4 — 외부 채팅 1차 흡입 (2시간)

§7 파이프라인 1회. 가공 .md 5~10개 → 종목/프로젝트 정착. 머지 → `v-kb-v2.2-phase4`

### Phase 5 — 운영 안착 (3시간)

- Dataview 동적화 (active projects 표, reverse index)
- `MAP.md` 5분 가이드
- 첫 lint — orphan/stale/missing concept/좌표 없는 raw read 0건/status 정합성
- 루트 `CLAUDE.md` 최종 확정 (skeleton + 운영 경험 반영)
- 머지 → `v-kb-v2.2-stable`

---

## 9. Phase E (별도, 본 v2.2 범위 외) — 3국 `.claude` 통합

> **사용자 결정**: 본 v2.2.x 범위 외. `S-anlyz/`, `S-anlyz-kr/`, `S-anlyz-jp/` 그대로 유지.

### 9.1 인터페이스 (v2.2 보장)

- 루트 `CLAUDE.md` 와 `S-anlyz*/CLAUDE.md` 는 이름·역할 분리 도메인. v2.2 어떤 단계에서도 분석 파이프 CLAUDE.md 미수정
- `60_AGENTS/` 폴더 금지
- v2.2 운영 중 발견되는 3국 차이는 `20_WIKI/projects/multi-agent-stock-analysis/LOG.md` 에 `## [YYYY-MM-DD] observation | agent-diff: ...`

### 9.2 Phase E 진입 트리거 (참고)

- v2.2 Phase 5 안착 후 최소 2주 운영 관찰
- A/B 비교 검증 (시범 국가 1개, 1주 분석 결과 동등성)
- 자세한 절차는 `PLAN_통합지식관리-리스크격리_260504.md` §Phase E

---

## 10. 사고 시 복구

| 사고 | 복구 명령 |
|---|---|
| "이번 phase 처음부터" | `git reset --hard <태그>` (예: `v-kb-v2.2-phase1`) |
| "Pilot 결과 부적절" | `git reset --hard v-kb-v2.2-phase1` (phase2-pilot 통째 폐기) → v2.3 plan 수정 |
| "방금 자산 1개 이동만 무효화" | `git revert <commit-hash>` (자산 단위 1커밋이라 단일 종목만 영향) |
| "방금 프로젝트 1개 이동만 무효화" | 동 |
| "브랜치 통째 폐기" | `git checkout master && git branch -D kb-v2.2/<branch>` |
| "PC 망가짐" | 다른 PC `git clone <원격URL>` |
| "wiki 페이지 LLM 잘못 갱신" | `git checkout HEAD~1 -- <path>` 후 재작성 의뢰 |
| "Phase E 통합 후 분석 회귀" | `git checkout master` 1줄 |
| "synthesis.md 분석 복제처럼 비대" | lint → 식별 → 트리밍 + concepts/themes 분산 |
| "프로젝트 status 잘못 표시" | INDEX.md frontmatter 직접 수정 + LOG `status-change` |

---

## 11. 검증 체크리스트

| Phase | 통과 기준 |
|---|---|
| 0 | `git tag v-pre-kb-v2.2`, 원격 동기화 |
| 1 | Obsidian 볼트 열림, `10_*` `20_*` `90_*` 폴더 진입, 루트 `CLAUDE.md` 에 §6.0 + Mirror + Status Vocabulary 포함, 템플릿 9종 작동 |
| **2-pilot** | MSFT raw 이관, knowledge-management raw 이관, git log 단위 식별 |
| **3-pilot** | 위 1+1 wiki 부트, plan-document 가이드 작성, concept 2~3개 stub, **분석/문서 복제 0건** |
| **Pilot Gate** | §8 게이트 9항 모두 합격 |
| 2-full | 나머지 자산·프로젝트 raw 이관, git log 단위 식별 가능 |
| 3-full | 소스 스키마 가이드 7종 (pilot 1 + full 6), Asset/Project Tier 3 + Tier 2 모두 부트, **분석/문서 복제 0건** |
| 4 | `10_RAW/chats/.../raw.json` 미커밋, 가공 .md 5+ 정착, 각 ingest 좌표 또는 "none" 기록 |
| 5 | Dataview 동적 표 작동, 첫 lint 보고서, **좌표 없는 raw read 0건**, **status 정합성 100%**, `MAP.md`, 루트 `CLAUDE.md` 확정 |

---

## 12. 즉시 실행 가능한 첫 액션 (★ v2.2.1 갱신)

### 권장: Pilot-first

```
세션 1 (~3h, 한 번에 가능)
├── Phase 0           (30분)
└── Phase 1           (2.5h) → v-kb-v2.2-phase1 태그

세션 2 (~2h, 다른 날 가능)
├── Phase 2-pilot     (1h) — MSFT 1개 + knowledge-management 1개만
├── Phase 3-pilot     (1h) — 위 1+1 wiki + plan-document 가이드 + concepts 2~3개
└── Pilot 검증 게이트   ★

  ↓ 합격 (대부분 케이스)
세션 3~4 (~8h, 분할 가능)
├── Phase 2-full      (4h, 자산·프로젝트 단위 분할 커밋)
└── Phase 3-full      (4h, 소스 가이드 6종 + 나머지 wiki)

  ↓ 합격
세션 5+ (한 주 띄움)
├── Phase 4           (2h)
└── Phase 5           (3h)
```

**총 ~16h, 5+ 세션 분할**. 이전 v2.2.0 의 일괄 13h 대비 +3h(검증 비용)지만 사고 비용↓.

### 대안

- **A안 (보수)**: Phase 0 + 1만 (3h). 골격만 만들고 운영은 미루기
- **C안 (적극, 비권장)**: Phase 0~5 일괄 (~16h, 1세션). 비개발자 + Auto mode 환경에서 컨텍스트 한계로 비권장

---

## 13. 향후 확장 (v2.2 안착 후)

13.1 검색 인프라 (qmd CLI) — 페이지 100개+ 시
13.2 Marp 슬라이드 — Obsidian 플러그인
13.3 Supabase 3차 색인 — 종목 50개+ 시
13.4 Phase E (`.claude` 통합) — §9
13.5 Raw 자동 좌표 추출 — ingest 시 raw 목차 스캔으로 좌표 후보 제안
13.6 Project 진척 시각화 — Mermaid/Excalidraw

---

## 부록 A — 루트 CLAUDE.md 골격

> **v2.2.1 분리**: 본문에서 외부 파일로 이전. 갱신은 별도 진행.
>
> → `archive/REF_CLAUDE-md_skeleton_260505.md`

골격 핵심 7개 항목 (외부 파일 미접근 시 baseline):
1. **Folder ↔ Layer Mapping** binding (10_*=Raw, 20_*=Wiki, _templates/+CLAUDE.md=Schema)
2. **Two Axes** (Asset / Project) + 공유 폴더 명시
3. **3-Tier Navigation** (root / axis INDEX·LOG / item)
4. **Rules 7개** (raw 미수정, S-anlyz 미수정, INDEX 우선, LOG append, frontmatter 필수, 교차참조 의무, 분석/문서 복제 금지)
5. **Raw Reading Discipline** (좌표 필수, sources 가이드 참조, 자유 탐색 금지, LOG 좌표 기록)
6. **Mirror Principle** (.md only Wiki, mirrors_raw frontmatter 필수)
7. **Status Vocabulary + LOG Event Vocabulary** binding

---

## 부록 B — Obsidian 추천 플러그인

| 플러그인 | 용도 | 필수도 |
|---|---|---|
| Dataview | active 표·reverse index 동적 생성 | ★★★ (Phase 5) |
| Templater | frontmatter 자동 채움 | ★★★ (Phase 1) |
| Tag Wrangler | 태그 통합 | ★★ |
| Excalidraw | 다이어그램 | ★ |
| Git | 백업 | ★★ |
| Marp | 슬라이드 | ★ (확장) |

---

## 부록 C — 네이밍 규칙

- 종목 폴더: `<국가>-<티커>` (예: `US-MSFT`)
- 프로젝트 슬러그: kebab-case 영문 (`knowledge-management`, `multi-agent-stock-analysis`, `screening-mode`)
- 자산 raw: `10_RAW/assets/<티커>/reports/dashboard_<YYMMDD>.{jsx,html}`, `SOURCE_PACKAGE_<YYMMDD>.json`
- 프로젝트 raw: `10_RAW/projects/<slug>/{plans,results,handoffs,chats,clippings}/`
  - plan: `PLAN_<주제>_v<MAJOR.MINOR.PATCH>_<YYMMDD>.md`
  - result: `RESULT_<주제>_<YYMMDD>.md`
  - handoff: `HANDOFF-<seq>_<YYMMDD>.md`
- 스크리닝 raw: `10_RAW/screening/<YYYYMMDD>/<COUNTRY>_스크리닝.html`
- Wiki: `20_WIKI/{assets,projects}/<item>/{INDEX,synthesis,decisions}.md`
- 개념·테마·비교: `20_WIKI/{concepts,themes,comparisons}/<kebab>.md`
- 소스 스키마: `20_WIKI/concepts/sources/<country>-<type>-structure.md`, `plan-document-structure.md`
- Lint 보고서: `90_ARCHIVE/lint-reports/lint-report-<YYMMDD>.md`
- Git 태그: `v-kb-v2.2-<phase>`, `v-kb-v2.2-stable`
- Git 브랜치: `kb-v2.2/<phase-name>` (예: `kb-v2.2/phase2-pilot`)

---

## 부록 D — v2.2.0 → v2.2.1 마이그레이션

- v2.2.0 어떤 Phase도 시작되지 않았으므로 v2.2.1 Phase 0 부터 시작 가능
- v2.2.0 Phase 1 진행됐다면:
  - 루트 `CLAUDE.md` 골격 `REF_CLAUDE-md_skeleton_260505.md` 외부 파일 참조 갱신 (선택)
  - Phase 2/3 작업 미시작이면 v2.2.1 의 pilot 분할로 진행
- v2.2.0 Phase 2 진행됐다면 그대로 진행 (Phase 분할은 추가 안전책일 뿐, 일괄 진행도 유효)

---

## 부록 E — Source Schema Guide 작성 가이드 (Phase 3 산출물, 7종)

`_templates/source-structure.md` 템플릿. 표준 구조:

```markdown
---
type: source-structure
country: US | KR | JP | global
source: sec-10k | sec-10q | investing-transcript | dart-yusil | edinet-yuho | source-package | plan-document
date: 2026-05-05
status: stable
---

# {Source Name} 구조 가이드

## 목적
LLM이 {source} 파일 read 전 좌표(연도 × Item)를 정하기 위한 참조. Raw Reading Discipline 운영 전제.

## 파일 형태
- 포맷: HTML | JSON | PDF | MD
- 일반 위치
- 평균 토큰 규모

## 섹션·Item 구조
| Item/섹션 | 1줄 요약 | 우리 분석 활용 |

## 좌표 통보 형식 예시
- "MSFT FY2025 10-K Item 7 MD&A only"
- "PLAN v2.2.1 §6.0~§6.3 only"

## 관련 Concept/Theme 백링크
```

7종 (Phase 3-pilot 1종 + Phase 3-full 6종):
1. **`plan-document-structure.md`** ★ Phase 3-pilot
2. `us-sec-10k-structure.md`
3. `us-sec-10q-structure.md`
4. `us-investing-transcript-structure.md`
5. `kr-dart-yusil-structure.md`
6. `jp-edinet-yuho-structure.md`
7. `source-package-schema.md`

각 1~2 페이지. **본문 인용 금지**. 구조와 좌표 어휘만.

---

## 부록 F — Project 슬러그 사전

| 슬러그 | 범위 | 포함 raw |
|---|---|---|
| `knowledge-management` | 본 vault 자체 설계·운영 | `archive/PLAN_통합지식관리체계_*.md`, `archive/PLAN_통합지식관리-리스크격리_*.md`, `archive/REF_CLAUDE-md_skeleton_*.md`, `llm-wiki.md` (외부 출처) |
| `multi-agent-stock-analysis` | S-anlyz 시스템 (3국 공통) | `S-anlyz/plan*.md`, `S-anlyz/research-v5.md`, `S-anlyz/GOTCHAS.md`, `S-anlyz-kr/HANDOFF-1.md`, agent/skill 변경 plan |
| `screening-mode` | 스크리닝 모드 (multi-agent의 sub 또는 분리 — 일단 분리) | `S-anlyz-kr/archive/PLAN_jp-sync-screening-cyclical.md`, 스크리닝 plan/result |

**HANDOFF 분류**: 주 프로젝트 1개 매핑 + 다른 프로젝트 INDEX 백링크. 모호 시 `90_ARCHIVE/handoffs/`. 새 HANDOFF는 frontmatter `project:` 강제.
