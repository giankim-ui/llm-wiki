# PLAN — 통합 투자 지식 관리 체계 v2.2.0

- **작성일**: 2026-05-05
- **이전 버전**: v2.1.0 (260505), v2.0.0 (260504), v1.0 (260504), 리스크격리 보완본 (260504)
- **반영 이론**: `llm-wiki.md` (LLM-as-wiki-maintainer 패턴)
- **대상 자산**: AI 채팅 기록 + JSX/HTML 분석 산출물(국가별) + plan*/result*/handoff* 운영 문서 + 캡처/스터디 자료
- **목표**: 흩어진 자료를 **"compounding 가능한 단일 지식 베이스"** 로 통합 — 사용자는 사고하고, LLM은 유지보수한다

---

## 0. v2.2.0 변경 요약 (v2.1.0 대비)

본 버전은 v2.1.0의 **단일 축(Asset only) 한계**를 발견하고 운영 navigation 까지 확장한 결과다. v2.1.0은 분석 인사이트(asset wiki)에는 정밀했으나 사용자의 다른 핵심 pain — "지금 진행중 프로젝트 뭐?", "이거 끝났나?", "비슷한 거 전에 했나?" — 을 다루지 못했다.

| 영역 | v2.1.0 | v2.2.0 |
|---|---|---|
| **데이터 축** | Asset only (종목 분석 산출물 중심) | **Asset + Project dual axis**. plan/result/handoff 도 1급 raw |
| **Vault 구성** | 단일 vault | **단일 vault 유지 (확정)**. cross-axis wikilink·graph 활용 — 분리 vault 검토 후 dual axis 결합도 강해 단일 채택 |
| **Navigation 구조** | 단일 INDEX/LOG 루트 | **3-tier**: root dashboard / axis INDEX·LOG / item detail |
| **Status 추적** | 비공식 (frontmatter `status: draft\|active\|done`) | **5단계 binding 어휘** (`active\|blocked\|paused\|done\|archived`) + `last_activity`/`current_phase`/`blocker`/`done_criteria` 필수 |
| **검색 방식** | 페이지 본문 grep | **Concept/Theme reverse index** — "어느 concept이 어느 프로젝트에서 다뤄졌나" 역색인 자동 유지 |
| **운영 pain 해결** | 분석 인사이트만 | **navigation pain 직접 해결**: 활동 active 정렬, 종료 여부 명시, 유사 프로젝트 검색 |
| **Wiki 가치 정의** | "compounding investment thesis" | **+ "compounding methodology"** — 프로젝트 wiki는 메타 인사이트 (왜 이렇게 결정했나) 누적 |

> v2.1.0 → v2.2.0 마이그레이션: v2.1.0 어떤 Phase도 시작되지 않은 상태이므로 v2.2.0 Phase 0 부터 그대로 시작 가능. v2.0.0/v2.1.0 은 archive에 보존.

---

## 1. 이론적 토대

### 1.1 RAG vs Wiki — 결정적 차이

기존 NotebookLM/ChatGPT 업로드 방식은 **RAG(Retrieval-Augmented Generation)**: 질문 시점에 원자료에서 청크를 검색 → 매번 처음부터 합성. **누적이 없다.**

LLM-Wiki는 다르다: LLM이 원자료를 한 번 읽으면 **wiki에 영구 통합**한다 — 엔티티 페이지를 갱신하고, 모순을 표시하고, 종합문을 갱신한다. **wiki는 점점 풍부해지는 compounding artifact**.

**우리 케이스에 대입**:
- Asset 측: `MSFT_분석대시보드.html`은 1회성 산출물 → 다음 분기에 인사이트 자동 누적 안 됨
- Project 측: `PLAN_통합지식관리체계_v2.1.0_260505.md` 결정 근거가 archive에 묻혀 다음 plan 작성 시 같은 함정 반복 가능
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

→ 두 축은 **공유 concept** 으로 연결됨. 예: `cyclical-scoring` 는 multi-agent-stock-analysis 프로젝트 산출물이자 자산 분석 도구. 한 vault에서 양쪽이 데이터 포인트를 적립.

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
│   ├ projects/<프로젝트>/   (Project axis) ★ v2.2 신규          │
│   ├ concepts/, themes/, comparisons/   (cross-axis 공유)      │
│   └ industry/, macro/, frameworks/, methodology/, screening/  │
└──────────────────────────────────────────────────────────────┘
            ↑ "이 시점 그 사실"의 immutable
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Raw   /10_RAW/  (immutable, 다양 포맷)               │
│   ├ assets/<티커>/   (.jsx/.html/.json/.md)                   │
│   ├ projects/<프로젝트>/   (.md plan/result/handoff) ★ v2.2 신규 │
│   ├ screening/, chats/, clippings/, docs/, attachments/, inbox/ │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 계층별 운영 원칙

**Layer 1 — Raw (`10_RAW/`)**:
- LLM 수정 금지. 영구 보존
- `S-anlyz*/!Report/` JSX/HTML도 raw (분석 파이프 결정적 산출물 = "이 시점 종목 사진"). 다시 만들 수 있어도 그 시점은 immutable
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
- 볼트 루트 `CLAUDE.md` 신규 작성
- `S-anlyz*/CLAUDE.md`, `S-anlyz*/.claude/` **건드리지 않음** (분석 파이프 정책 = 별도 도메인)

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
| `10_RAW/projects/knowledge-management/plans/PLAN_v2.2.0_260505.md` | `20_WIKI/projects/knowledge-management/synthesis.md` 의 plan-version 항목 |
| `10_RAW/projects/knowledge-management/handoffs/HANDOFF-3.md` | 해당 프로젝트 INDEX의 handoff 표 + concept 추출 |
| `10_RAW/screening/20260503/US_스크리닝.html` | `20_WIKI/screening/260503_us-cyclical-themes.md` |
| `10_RAW/chats/claude/2026-04/raw.json` (gitignored) | `10_RAW/chats/claude/2026-04/_processed/<주제>.md` + 해당 종목/프로젝트 페이지 갱신 |

**원칙**: "Obsidian 그래프·검색에 들어가야 하는 정보는 LLM이 .md 미러를 만든다. 원본은 raw에 immutable artifact 로 둔다. 미러본에는 항상 원본 wikilink 포함."

---

## 3. 폴더 트리 (v2.2.0 정본)

```
!claudeProject/                          ← Obsidian 볼트 루트
│
├── CLAUDE.md                            ★ 볼트 스키마
├── INDEX.md                             ★ Tier 1 dashboard (5초 진입)
├── LOG.md                               ★ Tier 1 cross-axis 최근 30일 highlight
├── MAP.md                               사람용 가이드
│
├── 10_RAW/                              ★ Layer 1 통째 — LLM 수정 금지
│   ├── assets/                          (Asset axis raw)
│   │   └── <COUNTRY>-<TICKER>/
│   │       ├── reports/                 .jsx, .html, .json
│   │       ├── chats/                   .md (종목 관련 chat 정착)
│   │       ├── clippings/               .md
│   │       └── docs/                    .md
│   ├── projects/                        ★ Project axis raw — v2.2 신규
│   │   └── <project-slug>/
│   │       ├── plans/                   PLAN_*.md (immutable)
│   │       ├── results/                 RESULT_*.md
│   │       ├── handoffs/                HANDOFF*.md
│   │       ├── chats/                   .md (프로젝트 관련 chat)
│   │       └── clippings/               .md
│   ├── screening/<YYYYMMDD>/            US/KR/JP 카드 .html, equity_ratios.json
│   ├── chats/
│   │   ├── claude/<YYYY-MM>/raw.json    (gitignored)
│   │   ├── gemini/<YYYY-MM>/raw.json    (gitignored)
│   │   └── _processed/                  종목/프로젝트 분리 후 정착 대기
│   ├── clippings/                       종목·프로젝트 미분류 일반 자료
│   ├── docs/                            archive .md 일반
│   ├── attachments/                     이미지·PDF
│   └── inbox/                           분류 전 임시
│
├── 20_WIKI/                             ★ Layer 2 통째 — LLM 단독, .md only
│   ├── assets/                          (Asset axis wiki)
│   │   ├── INDEX.md                     ★ Tier 2 자산 풀 카탈로그
│   │   ├── LOG.md                       ★ Tier 2 자산 ingest/query/lint chronological
│   │   └── <COUNTRY>-<TICKER>/
│   │       ├── INDEX.md                 ★ Tier 3 종목 허브
│   │       ├── synthesis.md             compounding 5~10줄 Δ
│   │       └── decisions.md             사용자 매수·매도 결정
│   ├── projects/                        ★ Project axis wiki — v2.2 신규
│   │   ├── INDEX.md                     ★ Tier 2 프로젝트 풀 카탈로그 (status별 그룹)
│   │   ├── LOG.md                       ★ Tier 2 프로젝트 chronological events
│   │   └── <project-slug>/
│   │       ├── INDEX.md                 ★ Tier 3 프로젝트 허브
│   │       ├── synthesis.md             phase·version Δ 5~10줄
│   │       └── decisions.md             사용자 설계 결정
│   ├── concepts/                        ★ cross-axis 공유 도메인·패턴 엔티티
│   │   ├── INDEX.md                     concept 카탈로그 + reverse index
│   │   ├── pbr.md, economic-moat.md, cyclical-investing.md, fcf.md, ...
│   │   ├── llm-wiki-pattern.md, mirror-principle.md, raw-reading-discipline.md, ...
│   │   └── sources/                     소스 스키마 가이드 (Raw Reading 좌표용)
│   │       ├── us-sec-10k-structure.md, us-sec-10q-structure.md
│   │       ├── us-investing-transcript-structure.md
│   │       ├── kr-dart-yusil-structure.md, jp-edinet-yuho-structure.md
│   │       ├── source-package-schema.md
│   │       └── plan-document-structure.md   ★ v2.2 신규
│   ├── themes/                          cross-axis 투자 테마 + 프로젝트 테마
│   │   ├── INDEX.md
│   │   ├── ai-capex-burden.md, rate-cycle-2026.md, ...
│   │   └── km-thesis-evolution.md, agent-architecture-evolution.md
│   ├── comparisons/                     명시적 비교 분석 (양 축 공유)
│   │   ├── INDEX.md
│   │   ├── msft-vs-googl-cloud-margin.md
│   │   └── km-plans-v1-v2.0-v2.1-v2.2.md
│   ├── industry/, macro/                업종·거시
│   ├── frameworks/                      방법론
│   ├── methodology/                     query 산출물 file-back
│   └── screening/                       cross-screening 인사이트
│
├── 90_ARCHIVE/                          은퇴 자료 (Layer 1 취급)
│   ├── handoffs/                        프로젝트 미분류 일반 HANDOFF*.md
│   └── lint-reports/                    월간 lint 보고서
│
├── _templates/                          Templater 템플릿
│   ├── asset-INDEX.md, asset-synthesis.md
│   ├── project-INDEX.md, project-synthesis.md   ★ v2.2 신규
│   ├── concept.md, theme.md, comparison.md
│   ├── source-structure.md
│   ├── plan.md, chat-extract.md
│
├── S-anlyz/, S-anlyz-kr/, S-anlyz-jp/   (기존 유지 — Phase E에서만 다룸)
│
└── .obsidian/                           Obsidian 설정
```

### 3.1 v2.1.0 대비 폴더 변경점

| 변경 | 이유 |
|---|---|
| **`10_RAW/projects/<slug>/`** 신설 | Project axis raw. plan/result/handoff 1급 자료화 |
| **`20_WIKI/projects/<slug>/`** 신설 | Project axis wiki. compounding methodology |
| **`20_WIKI/projects/INDEX.md`, `LOG.md`** 신설 | Tier 2 프로젝트 navigation 풀 카탈로그·시간선 |
| **`20_WIKI/assets/INDEX.md`, `LOG.md`** 신설 | Tier 2 자산 navigation (v2.1은 Tier 3만 존재) |
| **`20_WIKI/concepts/INDEX.md`, `themes/INDEX.md`, `comparisons/INDEX.md`** 신설 | reverse index 운영 |
| `20_WIKI/concepts/sources/plan-document-structure.md` 신설 | plan/result/handoff 좌표 가이드 (Raw Reading Discipline) |
| `20_WIKI/plans/active|done/` **폐기** | plan은 raw immutable. wiki 층은 `20_WIKI/projects/<slug>/` 가 담당 |
| 루트 `INDEX.md` 역할 변경 | Tier 1 dashboard (5초 진입). 풀 카탈로그가 아니라 top-of-mind |
| 루트 `LOG.md` 역할 변경 | Tier 1 cross-axis highlight. 풀 history는 axis LOG에 |
| `_templates/` `project-INDEX`, `project-synthesis` 추가 | 프로젝트 부트스트랩용 |

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
- [[20_WIKI/projects/knowledge-management/INDEX]] — v2.2.0 작성 중 · 2026-05-05
- [[20_WIKI/projects/multi-agent-stock-analysis/INDEX]] — 운영 안정 · 2026-05-03
- [[20_WIKI/projects/screening-mode/INDEX]] — 운영 안정 · 2026-04-28

### Recent Asset Activity (5 most recent)
- US-MSFT — analyzed 2026-05-03
- US-MOS — analyzed 2026-05-01
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

```markdown
# Vault Recent Activity (Last 30 Days)

> 상세: [[20_WIKI/projects/LOG]] · [[20_WIKI/assets/LOG]]

## [2026-05-05 22:00] knowledge-management v2.2.0 plan-version (★)
## [2026-05-05 18:00] knowledge-management v2.1.0 plan-version
## [2026-05-03] US-MSFT 분기 분석 ingest
## [2026-05-01] US-MOS 분기 분석 ingest
## [2026-04-28] screening-mode US 스크리닝 phase-complete
...
```

LLM 운영: ingest 시 highlight 여부 판단 (plan-version, phase-start/complete, status-change, 자산 분기 분석 = highlight). lint 가 noise 판단 시 정리.

### 4.3 Tier 2 — `20_WIKI/projects/INDEX.md` (★ pain 직접 해결)

```markdown
---
type: index
scope: projects
updated: 2026-05-05 22:00
maintained_by: claude-code
---

# Projects Index

## ★ Active (최근 활동 30일 이내)
| Project | Status | Last Activity | Current Phase/Version | Blocker |
|---|---|---|---|---|
| [[knowledge-management/INDEX\|knowledge-management]] | active | 2026-05-05 | v2.2.0 작성 / Phase 0 대기 | — |
| [[multi-agent-stock-analysis/INDEX\|multi-agent-stock-analysis]] | active | 2026-05-03 | 운영 안정 | — |
| [[screening-mode/INDEX\|screening-mode]] | active | 2026-04-28 | 운영 안정 | — |

## Blocked / Waiting (외부 의존)
| Project | Status | Blocker | Last Activity |

## Paused (사용자 의도 중단)
| Project | Paused Since | Reason | Resume Trigger |

## Recently Done (지난 90일)
| Project | Done At | Outcome | Key Concepts Yielded |

## Archived (90일+ 또는 폐기)
- (오래된 것)

---

## ★ Concept Reverse Index ("비슷한 거 했나?" 해결)
| Concept | Projects |
|---|---|
| [[../concepts/llm-wiki-pattern]] | knowledge-management |
| [[../concepts/mirror-principle]] | knowledge-management |
| [[../concepts/raw-reading-discipline]] | knowledge-management |
| [[../concepts/agent-orchestration]] | multi-agent-stock-analysis |
| [[../concepts/source-package-contract]] | multi-agent-stock-analysis |
| [[../concepts/cyclical-scoring]] | multi-agent-stock-analysis, screening-mode |
| [[../concepts/asset-value-7step]] | multi-agent-stock-analysis, screening-mode |

## Theme Index
- [[../themes/km-thesis-evolution]]
- [[../themes/agent-architecture-evolution]]
```

### 4.4 Tier 2 — `20_WIKI/projects/LOG.md` (chronological)

```markdown
# Projects Log

## [2026-05-05 22:00] decision | knowledge-management
- Decision: dual-axis 도입 + 3-tier navigation
- Driver: 사용자 navigation pain (active 프로젝트·완료 여부·유사 프로젝트 검색)
- Affected: PLAN v2.2.0 신규 작성

## [2026-05-05 18:00] plan-version | knowledge-management
- Version: v2.1.0 (active)
- Δ vs v2.0.0: 폴더 prefix=Layer, Mirror Principle, Raw Reading Discipline, 소스 스키마 가이드 6종

## [2026-05-05 14:00] concept-extracted | knowledge-management
- New: [[../concepts/raw-reading-discipline]]
- Source: PLAN v2.1.0 §6.0
- Cross-project: multi-agent-stock-analysis 의 supervisor 수집 상한 규칙과 짝

## [2026-05-04 14:00] plan-version | knowledge-management
- v1.0 → v2.0.0
- Δ: LLM-Wiki theory absorbed, 60_AGENTS removed

## [2026-04-28 16:00] phase-complete | screening-mode
- Phase: US screening 운영 안정화
- Outcome: 카드 그리드 대시보드 안착
```

**LOG event vocabulary (binding)**:

| Event | 의미 |
|---|---|
| `decision` | 설계 결정 (왜 그렇게 하기로 했나) |
| `plan-version` | 새 PLAN_*.md raw 추가 |
| `result` | RESULT_*.md raw 추가 |
| `phase-start` / `phase-complete` | phase 전환 |
| `status-change` | active ↔ blocked ↔ paused ↔ done |
| `concept-extracted` | 새 concept 페이지 도출 |
| `theme-extracted` | 새 theme 페이지 도출 |
| `handoff` | 세션 인계 (HANDOFF*.md raw 추가) |

### 4.5 Tier 2 — `20_WIKI/assets/INDEX.md`

```markdown
---
type: index
scope: assets
updated: 2026-05-05
---

# Assets Index

## ★ Watchlist (모니터링 중)
| Asset | Country | Last Analyzed | Themes | Sector |

## Recently Analyzed (최근 30일)
| Asset | Date | Δ summary |

## Holdings (사용자 보유 — decisions.md 참조)
| Asset | Since | Last Review |

## All Assets (전체)
| Asset | Country | Last Analyzed | Status |

---

## Theme Reverse Index
| Theme | Assets |
| [[../themes/ai-capex-burden]] | US-MSFT, US-GOOGL, US-AMZN, US-META |
| [[../themes/shipping-supercycle]] | KR-005380, JP-9101 |

## Sector Reverse Index
| Sector | Assets |
```

### 4.6 Tier 2 — `20_WIKI/assets/LOG.md`

자산 ingest/query/lint chronological. 분기 cadence라 cross-asset 활동이 띄엄띄엄 — noise 적음.

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
status: active | blocked | paused | done | archived | draft | stable    # 항목별 적용 어휘 다름 (§5.2)
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

**Project (`type: project-index`)** — 5단계 (★ "끝났나?" 질문 항상 답 가능):

| Status | 정의 | 진입 조건 | 추가 frontmatter |
|---|---|---|---|
| `active` | 최근 30일 활동 / 진행 중 | 신규 또는 재개 | `last_activity`, `current_phase`, `done_criteria` |
| `blocked` | 외부 의존 대기 | 사용자 명시 | `blocker` (1줄) |
| `paused` | 사용자 의도적 중단 | 사용자 명시 | `paused_since`, `resume_trigger` |
| `done` | 목표 달성, 더 갱신 안 함 | done_criteria 충족 + 사용자 확인 | `done_at`, `outcome` |
| `archived` | 90일 done 후 또는 폐기 | 자동 또는 사용자 명시 | `archived_at` |

**Asset (`type: asset-index`)** — 3단계:
- `watchlist` (모니터링), `holding` (보유), `archived` (관심 종료)

**기타 페이지**:
- `concept`, `theme`, `comparison`, `framework`: `draft | stable`
- `plan` (raw에 있음): `active | done` (plan은 raw immutable이지만 어떤 plan이 현행인지는 표시)

### 5.3 Project 자동 갱신 규칙 (LLM 운영)

이벤트 발생 시 LLM이 자동 갱신:
- 새 plan 작성 → `current_version` 갱신, `plan-version` LOG event
- phase 시작 → `current_phase` 갱신, `phase-start` LOG event
- 30일 활동 없음 → lint 가 status 정합성 확인 제안 (자동 변경 X)

`status` 변경은 **항상 사용자 confirm**. LLM은 제안만.

### 5.4 Dataview 활용 예시 (Phase 5)

```dataview
TABLE status, last_activity, current_phase, blocker
FROM "20_WIKI/projects"
WHERE type = "project-index" AND status = "active"
SORT last_activity DESC
```

→ projects/INDEX.md 의 active 표가 자동 생성.

---

## 6. 4대 오퍼레이션 — Reading Discipline / Ingest / Query / Lint

### 6.0 Raw Reading Discipline (모든 오퍼레이션 전제)

**원칙**: `10_RAW/` 의 .json/.html/.md 파일은 **좌표(연도 × Item/섹션) 없이 통째로 Read 하지 않는다**.

**Asset 축 좌표 어휘**:
- "MSFT FY2025 10-K Item 7 MD&A"
- "005380 2024 사업보고서 재무에 관한 사항"

**Project 축 좌표 어휘**:
- "PLAN_통합지식관리체계_v2.1.0_260505.md §6.0~§6.3"
- "PLAN_통합지식관리체계_v2.1.0_260505.md 부록 A 만"
- "RESULT_<주제>_<날짜>.md 결론 섹션"

**좌표가 정해지는 경로**:
1. 사용자 직접 통보
2. 분석 파이프 결과 메시지 / plan 작성 시 사용자가 통보하는 Δ
3. wiki에 이미 distilled — `synthesis.md` 또는 `concepts/` 에서 충당

**좌표 모를 때**: `20_WIKI/concepts/sources/{country}-{type}-structure.md` 또는 `plan-document-structure.md` 참조 → 후보 좌표 1~2개 결정 → 그래도 모르면 사용자에게 좌표 요청. 자유 탐색 raw read 절대 금지.

**위반 사례 (재발 금지)**: MOS 분석 시 21년 10-K 통째 read → 컨텍스트 폭주.
- **Plan 통째 read도 무시 못 함** — v2.2.0 plan ~30KB, 5개 plan 통째 read = 150KB
- supervisor 수집 상한(7/6/6)은 ingest 보호. 본 Discipline 은 query/synthesis 보호. 두 보호막 동시 작동

**lint에서 검출**: LOG.md raw read 좌표 기록 누락 시 lint 실패.

### 6.1 Ingest

**Trigger**: 사용자가 "이 자료 흡수해줘" 또는 분석 파이프/사용자가 새 raw 파일 떨어뜨림.

**Workflow**:
1. raw 파일이 `10_RAW/` 어디에 안착했는지 확인 (assets/ vs projects/ vs chats/ ...)
2. **사용자/파이프로부터 좌표 + Δ 통보 받음**
3. raw 통째 Read 금지. 좌표 부분만 핀포인트 Read
4. 갱신 대상 페이지 결정 (n개 propagation):

   **Asset ingest 시**:
   - `20_WIKI/assets/<티커>/synthesis.md` compounding 항목 append
   - `20_WIKI/assets/<티커>/INDEX.md` Last Analyzed 갱신
   - `20_WIKI/assets/INDEX.md` Recently Analyzed 갱신
   - `20_WIKI/assets/LOG.md` append
   - 관련 `concepts/<...>.md`, `themes/<...>.md`, `comparisons/<...>.md` 데이터 포인트 갱신
   - 루트 `INDEX.md` Recent Asset Activity 갱신
   - 루트 `LOG.md` highlight 판단

   **Project ingest 시 (예: 새 plan-version)**:
   - `20_WIKI/projects/<slug>/synthesis.md` plan-version 항목 append (5~10줄 Δ)
   - `20_WIKI/projects/<slug>/INDEX.md` `current_version`, `current_phase`, `last_activity` 갱신
   - `20_WIKI/projects/INDEX.md` Active 표 갱신 (status 자동 active 유지)
   - `20_WIKI/projects/LOG.md` append (`plan-version` event)
   - 도출 concept 있으면 `concepts/<new-concept>.md` 신규 작성 + `concepts/INDEX.md` reverse index 추가
   - 루트 `INDEX.md` Active Projects 정렬 갱신
   - 루트 `LOG.md` highlight (plan-version 은 항상 highlight)

5. 사용자에게 변경 페이지 목록 제시 → 확인 → 커밋

**예시: PLAN v2.2.0 ingest (이번 plan 자체의 self-ingest)**:
```
입력: 10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.2.0_260505.md
좌표: 본 plan §0~§6 (사용자 통보 — 본 plan 자체)
Δ:
  - dual axis (Asset + Project) 도입
  - 3-tier navigation
  - status taxonomy binding
  - concept reverse index
LLM raw read: §0 변경 요약만 (이미 알고 있는 내용이므로 0회도 가능)
영향:
  - 20_WIKI/projects/knowledge-management/synthesis.md  (plan-version 항목 append, 7줄)
  - 20_WIKI/projects/knowledge-management/INDEX.md      (current_version: v2.2.0)
  - 20_WIKI/projects/INDEX.md                            (KM 행 갱신)
  - 20_WIKI/projects/LOG.md                              (plan-version event append)
  - 20_WIKI/concepts/3-tier-navigation.md                (신규 concept)
  - 20_WIKI/concepts/status-taxonomy.md                  (신규 concept)
  - 20_WIKI/concepts/INDEX.md                            (reverse index 2건 추가)
  - 20_WIKI/comparisons/km-plans-v1-v2.0-v2.1-v2.2.md   (v2.2 행 추가)
  - 루트 INDEX.md, LOG.md
Token: raw read 0~1회, wiki write n=10 페이지
```

### 6.2 Query

**Workflow**:
1. **Navigation 질문 분기**:
   - "현재 active 프로젝트?" → `20_WIKI/projects/INDEX.md` 직진
   - "비슷한 거 했나? <키워드>" → `20_WIKI/projects/INDEX.md` Concept Reverse Index 또는 `20_WIKI/concepts/<키워드>.md` 의 cross-project 백링크
   - "MSFT 어땠나?" → `20_WIKI/assets/US-MSFT/INDEX.md`
   - 일반 질문 → 루트 `INDEX.md` → drill-down
2. raw 필요 시 §6.0 적용 (좌표 명시)
3. 답변 작성 + 출처 wikilink
4. 가치 있으면 wiki file-back:
   - 비교/연결 발견 → `20_WIKI/methodology/<주제>-<날짜>.md` 또는 `comparisons/<주제>.md`
   - LOG.md 에 query 기록

### 6.3 Lint (월 1회)

**체크 항목**:
| 검사 | 도구 |
|---|---|
| **좌표 없는 raw read** | LOG.md grep — 발견 시 lint 실패 |
| **synthesis.md 비대화** (asset/project 양쪽) | 항목당 평균 10줄 초과 → 복제 의심 |
| **status 정합성** | `status: active` 인데 `last_activity` 30일 초과 → 정정 제안 |
| **status: done 자동 archive 후보** | `done_at` 90일 초과 → archived 제안 |
| **Concept reverse index 누락** | `projects/<slug>/synthesis.md` 의 `concepts:` frontmatter 와 `concepts/INDEX.md` reverse 표 일치 확인 |
| **Theme reverse index 누락** | 동일 |
| 모순 검출 (cross-asset, cross-version) | LLM 교차 read |
| Stale: 6개월 갱신 없는 active 페이지 | frontmatter `date` |
| Orphan: inbound 링크 0 | Obsidian graph + grep |
| 누락 concept | 본문에 자주 등장하나 concepts/ 페이지 없음 |
| 누락 theme/comparison 후보 | 다수 종목·프로젝트 synthesis 가 같은 키워드 언급 시 자동 제안 |
| 깨진 링크 | Obsidian 자체 |
| Dead artifact: `10_RAW/` 미참조 | grep |

**산출물**: `20_WIKI/projects/LOG.md` + `20_WIKI/assets/LOG.md` 에 lint 항목 + `90_ARCHIVE/lint-reports/<날짜>.md` 상세.

---

## 7. 외부 채팅 Ingest 파이프라인

### 7.1 Claude.ai

1. 월 1회 Settings → Export data → JSON 다운로드
2. `10_RAW/chats/claude/<YYYY-MM>/raw.json` 저장 (gitignored)
3. Claude Code 요청: *"종목/프로젝트별 .md로 분리. 각 .md frontmatter `type: chat-extract, source: claude-chat, asset: <티커> | project: <slug>` 부여"*
4. LLM이 `10_RAW/chats/_processed/` 분리
5. 사용자가 가치 있는 5~10개 선별 → Ingest 워크플로 (§6.1) — 종목 관련은 `10_RAW/assets/<티커>/chats/`, 프로젝트 관련은 `10_RAW/projects/<slug>/chats/`, 일반 연구는 `20_WIKI/methodology/` 정착
6. raw.json 은 gitignore. 가공 .md 만 커밋

### 7.2 Gemini

Google Takeout → 동일.

### 7.3 자동화 (선택, Phase 5+)

PowerShell 폴더 감시 → `10_RAW/chats/.../raw.json` 자동 skill 호출. v2.2 본문 범위 외.

---

## 8. 리스크 격리 마이그레이션 (Phase 0~5)

> 비개발자 멘탈 모델: **"위험한 작업 = ① 커밋 ② 새 브랜치 ③ 푸시 + 태그"**.

### Phase 0 — 안전망 (30분)

- 현재 master `git status` M 정리 (남길 건 커밋, 버릴 건 사용자 명시 확인)
- 태그 `git tag v-pre-kb-v2.2`
- 푸시 `git push origin master --tags`
- 새 브랜치 `git checkout -b kb-v2.2/phase1-skeleton`

### Phase 1 — 골격 + 스키마 (2.5시간)

- **브랜치**: `kb-v2.2/phase1-skeleton`
- 작업:
  - `10_RAW/{assets,projects,screening,chats,clippings,docs,attachments,inbox}/` 빈 폴더
  - `20_WIKI/{assets,projects,concepts,themes,comparisons,industry,macro,frameworks,methodology,screening}/` 빈 폴더 + 각 INDEX.md (LOG.md는 axis만)
  - `20_WIKI/concepts/sources/` 빈 폴더
  - `90_ARCHIVE/{handoffs,lint-reports}/`, `_templates/`
  - `_templates/` 9종 템플릿 (asset-INDEX, asset-synthesis, **project-INDEX**, **project-synthesis**, concept, theme, comparison, source-structure, plan, chat-extract)
  - **루트 `CLAUDE.md` 작성** — 본 plan §1~6 압축본 + Raw Reading Discipline + Mirror Principle + Status Vocabulary
  - 빈 루트 `INDEX.md` (Tier 1 dashboard 골격), `LOG.md`, `MAP.md`
  - `.gitignore`: `10_RAW/chats/**/raw.json`, `10_RAW/chats/**/raw/`
- 검증: Obsidian 볼트 열림, 폴더 진입, 템플릿 작동, 루트 CLAUDE.md 에 §6.0 + Status Vocabulary 포함
- 머지 → `v-kb-v2.2-phase1`

### Phase 2 — Layer 1 자산·프로젝트 이관 (5시간)

- **브랜치**: `kb-v2.2/phase2-migration`
- 작업:

  **Asset raw 이관**:
  - `S-anlyz*/!Report/*.{jsx,html}` → `10_RAW/assets/<국가>-<티커>/reports/dashboard_<날짜>.{jsx,html}`
  - `S-anlyz*/raw/screening/*` → `10_RAW/screening/<YYYYMMDD>/`
  - `S-anlyz*/raw/<티커>/SOURCE_PACKAGE.json` 그대로 + `10_RAW/assets/<티커>/reports/` 에 복사

  **Project raw 이관 (★ v2.2 신규)**:
  - 프로젝트 슬러그 식별 (3개 사전 정의):
    - `knowledge-management`: `archive/PLAN_통합지식관리체계_*.md`, `archive/PLAN_통합지식관리-리스크격리_*.md`, `llm-wiki.md` (참고 raw)
    - `multi-agent-stock-analysis`: `S-anlyz/plan*.md`, `research-v5.md`, `S-anlyz/GOTCHAS.md`, `S-anlyz-kr/HANDOFF-1.md`, `S-anlyz-kr/archive/PLAN_jp-sync-screening-cyclical.md`
    - `screening-mode`: 스크리닝 관련 plan/result (multi-agent의 sub-project로 둘지 분리할지 사용자 결정 — 일단 분리)
  - root `HANDOFF-*.md` 분류 — 주 프로젝트 1개로 매핑, 분류 모호하면 `90_ARCHIVE/handoffs/`
  - 각 프로젝트로 `git mv`

  **Misc 이관**:
  - root 일반 `.md` → `10_RAW/docs/` 또는 적절 프로젝트
- 세이프티:
  - **`git mv` 사용**
  - **이관 단위당 1커밋** ("MSFT raw migration", "knowledge-management raw migration", ...)
  - 원본 폴더(`S-anlyz/!Report/`, `archive/`)는 **삭제하지 말고 유지** — 1주 병행 후 별도 cleanup phase
- 검증: 자산·프로젝트 raw 파일 더블클릭 정상, `git log --oneline` 식별 가능
- 머지 → `v-kb-v2.2-phase2`

### Phase 3 — Layer 2 부트스트랩 (5시간, 핵심)

- **브랜치**: `kb-v2.2/phase3-wiki-bootstrap`
- 작업 (LLM 자동 + 사용자 검토):

  **소스 스키마 가이드 7종 (먼저)**:
  - `20_WIKI/concepts/sources/us-sec-10k-structure.md`
  - `20_WIKI/concepts/sources/us-sec-10q-structure.md`
  - `20_WIKI/concepts/sources/us-investing-transcript-structure.md`
  - `20_WIKI/concepts/sources/kr-dart-yusil-structure.md`
  - `20_WIKI/concepts/sources/jp-edinet-yuho-structure.md`
  - `20_WIKI/concepts/sources/source-package-schema.md`
  - **`20_WIKI/concepts/sources/plan-document-structure.md`** ★ v2.2 신규 (project raw 좌표용)

  **Asset 부트스트랩**:
  - 종목별 `20_WIKI/assets/<티커>/INDEX.md` 자동 생성 (raw 메타 + SOURCE_PACKAGE URL 미러)
  - 종목별 `synthesis.md` stub 또는 5~10줄 추출 (분석 복제 금지)
  - `20_WIKI/assets/INDEX.md` 풀 카탈로그 + theme/sector reverse index
  - `20_WIKI/assets/LOG.md` bootstrap 항목

  **Project 부트스트랩 (★ v2.2 신규)**:
  - 프로젝트 3개 각 `20_WIKI/projects/<slug>/INDEX.md` (status, current_phase 등 frontmatter 완비)
  - 프로젝트 3개 각 `synthesis.md` — 기존 plan 1~3개의 plan-version 항목 5~10줄씩 (분석 복제 금지)
  - 프로젝트 3개 각 `decisions.md` 빈 파일 (사용자 작성 대기)
  - `20_WIKI/projects/INDEX.md` Active/Done 표 + Concept Reverse Index
  - `20_WIKI/projects/LOG.md` bootstrap (각 plan-version 항목 + concept-extracted 항목)

  **Concepts/Themes/Comparisons 부트**:
  - `20_WIKI/concepts/` stub 페이지 ~10개 — 도메인 (PBR/Cyclical/Moat/FCF/EPS quality), 패턴 (LLM-Wiki/Mirror Principle/Raw Reading Discipline/3-tier Navigation/Status Taxonomy)
  - `20_WIKI/concepts/INDEX.md` 카탈로그 + reverse index
  - `20_WIKI/themes/` stub 2~3 (km-thesis-evolution, agent-architecture-evolution)
  - `20_WIKI/comparisons/` 1개 (km-plans-v1-v2.0-v2.1-v2.2)

  **Tier 1 채우기**:
  - 루트 `INDEX.md` dashboard (Active Projects 3 + Recent Asset 5)
  - 루트 `LOG.md` highlight 부트
- 사용자 검토: 각 페이지 30초씩 훑어보고 "오류/사실관계"만 표시
- 머지 → `v-kb-v2.2-phase3`

### Phase 4 — 외부 채팅 1차 흡입 (2시간)

- **브랜치**: `kb-v2.2/phase4-chats`
- §7 파이프라인 1회 실행 — Claude.ai + Gemini 1개월
- 가공 .md 5~10개 → 종목/프로젝트 정착
- 머지 → `v-kb-v2.2-phase4`

### Phase 5 — 운영 안착 (3시간)

- **브랜치**: `kb-v2.2/phase5-ops`
- Obsidian Dataview 설치 → projects/INDEX.md, assets/INDEX.md 동적화 (Active 표 자동 생성, reverse index 자동 생성)
- `MAP.md` 5분 가이드
- **첫 lint 실행** — orphan/stale/missing concept/좌표 없는 raw read 0건/status 정합성
- 루트 `CLAUDE.md` 최종 확정
- 머지 → `v-kb-v2.2-stable`

---

## 9. Phase E (별도, 본 v2.2 범위 외) — 3국 `.claude` 통합

> **사용자 결정**: 본 v2.2.0 에서 다루지 않음. `S-anlyz/`, `S-anlyz-kr/`, `S-anlyz-jp/` 그대로 유지.

### 9.1 인터페이스 (v2.2 보장)

- 볼트 루트 `CLAUDE.md` 와 `S-anlyz*/CLAUDE.md` 는 **이름·역할 분리** 도메인. v2.2 어떤 단계에서도 분석 파이프 CLAUDE.md 미수정
- `60_AGENTS/` 폴더 **금지**. 추후 통합은 별도 폴더 또는 별도 저장소
- v2.2 운영 중 발견되는 3국 차이는 `20_WIKI/projects/multi-agent-stock-analysis/LOG.md` 에 `## [YYYY-MM-DD] observation | agent-diff: ...` 누적

### 9.2 Phase E 진입 트리거 (참고)

- v2.2 Phase 5 안착 후 최소 2주 운영 관찰
- A/B 비교 검증 (시범 국가 1개, 1주 분석 결과 동등성)
- 자세한 절차는 `PLAN_통합지식관리-리스크격리_260504.md` §Phase E 참조

---

## 10. 사고 시 복구

| 사고 | 복구 명령 |
|---|---|
| "이번 phase 처음부터" | `git reset --hard <태그>` (예: `v-kb-v2.2-phase1`) |
| "방금 파일 이동만 무효화" | `git revert <commit-hash>` |
| "브랜치 통째 폐기" | `git checkout master && git branch -D kb-v2.2/<branch>` |
| "PC 망가짐" | 다른 PC `git clone <원격URL>` |
| "wiki 페이지 LLM 잘못 갱신" | `git checkout HEAD~1 -- <path>` 후 재작성 의뢰 |
| "Phase E 통합 후 분석 회귀" | `git checkout master` 1줄 |
| "synthesis.md 분석 복제처럼 비대" | lint 1회 → 식별 → 트리밍 + concepts/themes 분산 |
| "프로젝트 status 잘못 표시" | `20_WIKI/projects/<slug>/INDEX.md` frontmatter 직접 수정 + LOG `status-change` event |

---

## 11. 검증 체크리스트

| Phase | 통과 기준 |
|---|---|
| 0 | `git tag` 에 `v-pre-kb-v2.2`, 원격 동기화 |
| 1 | Obsidian 볼트 열림, `10_*` `20_*` `90_*` 폴더 진입, 루트 `CLAUDE.md` 에 **§6.0 Discipline + Mirror + Status Vocabulary** 포함, 템플릿 9종 (project 2종 포함) 작동 |
| 2 | Asset raw 이관 정상, **Project raw 3개 슬러그 분리 완료** (knowledge-management, multi-agent-stock-analysis, screening-mode), git log 단위 식별 가능, 원본 보존 |
| 3 | 소스 스키마 가이드 **7종** 작성 (plan-document-structure 포함), Asset INDEX/synthesis 부트, **Project INDEX/synthesis/decisions 3세트 부트**, projects/INDEX.md status 표 + Concept Reverse Index 작동, 루트 `INDEX.md` dashboard 작동 (Active Projects 3개 표시), **분석/문서 복제 0건** |
| 4 | `10_RAW/chats/.../raw.json` 미커밋, 가공 .md 5+ 정착, **각 ingest 항목의 raw read 좌표 또는 "none" 기록**, 종목 vs 프로젝트 분류 정확 |
| 5 | Dataview 동적 표 (active projects + theme reverse index), 첫 lint 보고서, **좌표 없는 raw read 0건**, **status 정합성 100%**, `MAP.md` 5분 가이드, 루트 `CLAUDE.md` 운영 규칙 확정 |

---

## 12. 즉시 실행 가능한 첫 액션

1. **A안 (보수적)**: Phase 0 + Phase 1 — 안전망 + 골격. 약 3h
2. **B안 (중간, 권장)**: Phase 0~3 — 안전망 + 골격 + raw 이관 + **wiki 부트스트랩(자산+프로젝트 양 축) + 소스 스키마 가이드 7종**. 약 13h
3. **C안 (적극)**: Phase 0~5 — 채팅 흡입 + 운영 안착까지. 약 18h

비개발자 + Auto mode 환경에서는 **B안 (Phase 3까지)** 권장. v2.2의 핵심 가치(dual axis, 3-tier navigation, status taxonomy, concept reverse index)가 모두 작동하는 지점까지. Phase 4(채팅), Phase 5(Dataview/lint)는 한 주 띄워도 무방.

---

## 13. 향후 확장 (v2.2 안착 후)

### 13.1 검색 인프라 (qmd CLI)
페이지 100개 초과 시. BM25+벡터 하이브리드 + LLM 재랭킹.

### 13.2 Marp 슬라이드
Obsidian Marp 플러그인. wiki → 발표 자료.

### 13.3 Supabase 3차 색인
종목 50개 + 정형 쿼리 니즈 발생 시. frontmatter → row upsert.

### 13.4 Phase E (`.claude` 통합)
§9 참조.

### 13.5 Raw 자동 좌표 추출
ingest 시 raw 의 목차/소제목/Item 헤더만 한 번 스캔해 좌표 후보 자동 제안. Phase 5 이후.

### 13.6 Project 진척 시각화
Obsidian Mermaid 또는 Excalidraw — 프로젝트 phase timeline, decision tree 시각화.

---

## 부록 A — 루트 `CLAUDE.md` 골격 (Phase 1 작성 대상, v2.2 정본)

```markdown
# Vault CLAUDE.md (LLM-Wiki Schema v2.2)

This vault is an LLM-maintained dual-axis knowledge base. You are the maintainer.

## Folder ↔ Layer Mapping (BINDING)
- `10_*`, `90_*`, `_attachments/`, `S-anlyz*/`  → Layer 1 (Raw). NEVER modify.
- `20_*`, root `INDEX.md`/`LOG.md`/`MAP.md`  → Layer 2 (Wiki). LLM writes only. .md only.
- `/CLAUDE.md`, `_templates/`  → Layer 3 (Schema).

## Two Axes
- **Asset axis**: `10_RAW/assets/<COUNTRY>-<TICKER>/`, `20_WIKI/assets/<TICKER>/`
- **Project axis**: `10_RAW/projects/<slug>/`, `20_WIKI/projects/<slug>/`
- Shared: `20_WIKI/{concepts,themes,comparisons,industry,macro,frameworks,methodology,screening}/`

## 3-Tier Navigation
- Tier 1: `/INDEX.md` dashboard, `/LOG.md` cross-axis recent
- Tier 2: `20_WIKI/{projects,assets}/INDEX.md` + `LOG.md`
- Tier 3: `20_WIKI/{projects,assets}/<item>/INDEX.md`

## Rules
1. NEVER modify Layer 1 raw.
2. NEVER modify `S-anlyz*/CLAUDE.md` or `S-anlyz*/.claude/`.
3. ALWAYS read root `INDEX.md` for navigation queries; axis INDEX for axis-scoped queries.
4. ALWAYS append to LOG.md (axis-appropriate) after ingest/query/lint with `## [YYYY-MM-DD HH:MM] <event> | <subject>`.
5. ALWAYS ensure frontmatter on every .md.
6. NEVER skip cross-reference: ingest must touch INDEX.md(s) + LOG.md + ≥1 entity/concept/theme/comparison page besides item folder.
7. NEVER duplicate analysis/document content in wiki. synthesis.md = compounding log only (5~10 lines per item, Δ vs prior).

## Raw Reading Discipline (MOS Lesson — BINDING)
1. NEVER Read .json/.html/.md in `10_RAW/` in full. Coordinates first.
2. Coordinates = (item, version/date, section/Item).
3. If unknown, consult `20_WIKI/concepts/sources/...-structure.md`.
4. If still unclear, ASK user. Free-exploration full-read FORBIDDEN.
5. Each ingest's LOG entry must record raw read coordinates or "none".

## Mirror Principle
1. Information for Obsidian graph/search/Dataview must exist as .md in `20_WIKI/`.
2. Raw .jsx/.html/.json/.md stays in `10_RAW/`.
3. Wiki .md derived from raw must include `mirrors_raw: "[[10_RAW/...]]"` frontmatter.

## Status Vocabulary (BINDING)
- Project: `active | blocked | paused | done | archived`
- Asset: `watchlist | holding | archived`
- Concept/Theme/Comparison/Framework: `draft | stable`
- Plan (raw): `active | done`
- `status` change requires user confirm; LLM proposes only.

## LOG Event Vocabulary (BINDING)
decision, plan-version, result, phase-start, phase-complete, status-change, concept-extracted, theme-extracted, handoff, ingest, query, lint

## Workflows
- Reading Discipline: see PLAN v2.2.0 §6.0
- Ingest: §6.1
- Query: §6.2
- Lint: §6.3

## Frontmatter type Vocabulary
asset-index, asset-synthesis, project-index, project-synthesis, concept, theme, comparison, framework, plan, research, chat-extract, source-structure, handoff, log, index
```

---

## 부록 B — Obsidian 추천 플러그인

| 플러그인 | 용도 | v2.2 필수도 |
|---|---|---|
| Dataview | frontmatter 기반 동적 표 (status별 active 표, reverse index) | ★★★ (Phase 5) |
| Templater | 노트 생성 시 frontmatter 자동 채움 | ★★★ (Phase 1) |
| Tag Wrangler | 태그 통합 | ★★ |
| Excalidraw | 다이어그램 | ★ |
| Git | 볼트 백업 | ★★ |
| Marp | 슬라이드 출력 | ★ (확장) |

---

## 부록 C — 네이밍 규칙

- 종목 폴더: `<국가>-<티커>` (예: `US-MSFT`, `KR-005380`, `JP-5401`)
- 프로젝트 슬러그: kebab-case 영문 (예: `knowledge-management`, `multi-agent-stock-analysis`, `screening-mode`)
- 종목 산출물 (raw): `10_RAW/assets/<티커>/reports/dashboard_<YYMMDD>.{jsx,html}`
- 종목 SOURCE_PACKAGE: `10_RAW/assets/<티커>/reports/SOURCE_PACKAGE_<YYMMDD>.json`
- 프로젝트 plan (raw): `10_RAW/projects/<slug>/plans/PLAN_<주제>_v<MAJOR.MINOR.PATCH>_<YYMMDD>.md`
- 프로젝트 result (raw): `10_RAW/projects/<slug>/results/RESULT_<주제>_<YYMMDD>.md`
- 프로젝트 handoff (raw): `10_RAW/projects/<slug>/handoffs/HANDOFF-<seq>_<YYMMDD>.md`
- 스크리닝 산출물 (raw): `10_RAW/screening/<YYYYMMDD>/<COUNTRY>_스크리닝.html`
- 종목 wiki: `20_WIKI/assets/<국가>-<티커>/{INDEX,synthesis,decisions}.md`
- 프로젝트 wiki: `20_WIKI/projects/<slug>/{INDEX,synthesis,decisions}.md`
- 개념: `20_WIKI/concepts/<concept-kebab>.md`
- 소스 스키마: `20_WIKI/concepts/sources/<country>-<type>-structure.md` 또는 `plan-document-structure.md`
- 테마: `20_WIKI/themes/<theme-kebab>.md`
- 비교: `20_WIKI/comparisons/<a>-vs-<b>.md`
- Lint 보고서: `90_ARCHIVE/lint-reports/lint-report-<YYMMDD>.md`
- Git 태그: `v-kb-v2.2-<phase>`, `v-kb-v2.2-stable`
- Git 브랜치: `kb-v2.2/<phase-name>`

---

## 부록 D — v2.1.0 → v2.2.0 마이그레이션

본 v2.2.0 은 v2.1.0 을 **전면 대체**. v2.1.0 plan은 archive에 보존, 신규 작업은 v2.2 기준.

v2.1.0 → v2.2.0 마이그레이션 경로:
- v2.1.0 어떤 Phase도 시작되지 않았으므로 v2.2.0 Phase 0 부터 그대로 시작 가능
- v2.1.0 Phase 1 진행됐다면:
  - `10_RAW/projects/` 폴더 신규 추가
  - `20_WIKI/projects/` 폴더 + INDEX.md/LOG.md 신규 추가
  - `20_WIKI/assets/INDEX.md`, `LOG.md` 신규 추가 (axis Tier 2)
  - `20_WIKI/plans/active|done/` 폐기 → 내용을 적절한 프로젝트 raw로 이동
  - 루트 `INDEX.md`, `LOG.md` 재구성 (Tier 1 dashboard로)
  - 루트 `CLAUDE.md` 갱신 (Two Axes + 3-Tier Navigation + Status Vocabulary 추가)
- v2.1.0 Phase 2 진행됐다면 위에 더해 plan/result/handoff `git mv` 수행

---

## 부록 E — Source Schema Guide 작성 가이드 (Phase 3 산출물, 7종)

`_templates/source-structure.md` 템플릿 사용. 표준 구조:

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
이 가이드는 LLM이 {source} 파일을 읽기 전 좌표(연도 × Item)를 정하기 위한 참조다.
Raw Reading Discipline (CLAUDE.md §Raw Reading Discipline) 운영 전제.

## 파일 형태
- 포맷: HTML | JSON | PDF | MD
- 일반 위치: `10_RAW/assets/<티커>/reports/...` 또는 `10_RAW/projects/<slug>/plans/...`
- 평균 토큰 규모: ~~k tokens

## 섹션·Item 구조
| Item/섹션 | 내용 1줄 요약 | 우리 분석에서 자주 쓰는 용도 |

## 좌표 통보 형식 예시
- "MSFT FY2025 10-K Item 7 MD&A only"
- "PLAN v2.2.0 §6.0~§6.3 only"

## 관련 Concept/Theme 백링크
```

7종 가이드:
1. `us-sec-10k-structure.md` — Part I (Item 1/1A/1B/2/3) + Part II (Item 5/7/7A/8/9/9A) + III + IV
2. `us-sec-10q-structure.md` — Part I (Item 1/2/3/4) + Part II (Item 1/1A/2/6)
3. `us-investing-transcript-structure.md` — Prepared Remarks/Q&A/Participants, Investing/Motley/SA/ROIC 차이
4. `kr-dart-yusil-structure.md` — 사업의 내용/재무/이사회/주주/감사
5. `jp-edinet-yuho-structure.md` — 第一部 企業情報 (事業の状況/経理の状況) 등
6. `source-package-schema.md` — 내부 SOURCE_PACKAGE.json 구조
7. **`plan-document-structure.md`** ★ v2.2 신규 — 우리 표준 PLAN/RESULT/HANDOFF 구조 + § 어휘

각 가이드 1~2 페이지. **본문 인용 금지** (저작권 + 변동성). 구조와 좌표 어휘만 정리.

---

## 부록 F — Project 슬러그 사전 (Phase 2 분류 기준)

Phase 2에서 raw 이관 시 모호한 .md를 어디로 분류할지 판단 기준.

| 슬러그 | 범위 | 포함 raw 후보 |
|---|---|---|
| `knowledge-management` | 본 vault 자체 설계·운영 | `archive/PLAN_통합지식관리체계_*.md` (v1.0/v2.0.0/v2.1.0/v2.2.0), `archive/PLAN_통합지식관리-리스크격리_*.md`, `llm-wiki.md` (참고 raw, 외부 출처) |
| `multi-agent-stock-analysis` | S-anlyz 시스템 자체 (3국 공통) | `S-anlyz/plan*.md`, `S-anlyz/research-v5.md`, `S-anlyz/GOTCHAS.md`, `S-anlyz-kr/HANDOFF-1.md`, agent/skill 정의 변경 plan, supervisor 규칙 plan |
| `screening-mode` | US/KR/JP 스크리닝 모드 (multi-agent의 sub-project로 둘지 사용자 결정) | `S-anlyz-kr/archive/PLAN_jp-sync-screening-cyclical.md`, 스크리닝 관련 plan/result |

**HANDOFF 분류 원칙**:
- HANDOFF는 본질적 cross-cutting. **주 프로젝트 1개로 매핑** (가장 큰 비중) + 다른 프로젝트 INDEX에서 백링크
- 분류 모호 → `90_ARCHIVE/handoffs/` 일반 영역
- 새 HANDOFF 작성 시 frontmatter `project:` 필드 강제

**기존 root HANDOFF-1~6 분류 예시** (Phase 2 작업):
- HANDOFF-1: 내용 확인 후 KM 또는 multi-agent 매핑
- HANDOFF-2~6: 동일
- 모호 시 `90_ARCHIVE/handoffs/` + project 필드 누락
