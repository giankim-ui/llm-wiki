---
title: 통합 투자 지식 관리 체계 v2.1.0
date: 2026-05-05
tags: [plan, knowledge-management, investment, obsidian, v2.1.0]
---

# PLAN — 통합 투자 지식 관리 체계 v2.1.0

- **작성일**: 2026-05-05
- **이전 버전**: `PLAN_통합지식관리체계_v2.0.0_260504.md` (v2.0.0), `PLAN_통합지식관리체계_260504.md` (v1.0), `PLAN_통합지식관리-리스크격리_260504.md` (v1.0 보완)
- **반영 이론**: `llm-wiki.md` (LLM-as-wiki-maintainer 패턴)
- **대상 자산**: AI 채팅 기록(Claude/Gemini) + JSX/HTML 결과물(국가별) + archive 마크다운 + 캡처/스터디 자료
- **목표**: 흩어진 자료를 **"compounding 가능한 단일 지식 베이스"** 로 통합 — 사용자는 사고하고, LLM은 유지보수한다

---

## 0. v2.1.0 변경 요약 (v2.0.0 대비)

본 버전은 v2.0.0에 대한 4가지 추가 검토를 반영해 구조와 운영 원칙을 재정렬한 결과다.

| 영역 | v2.0.0 | v2.1.0 |
|---|---|---|
| **Layer ↔ 폴더 매핑** | 추상적 Layer 1/2/3, `10_ASSETS/` 안에 `_artifacts/`(L1) + `synthesis.md`(L2) 혼재 | **폴더 prefix가 곧 Layer**. `10_RAW/` = Layer 1 통째로, `20_WIKI/` = Layer 2 통째로. 한 폴더는 한 계층 |
| **Obsidian 호환성** | 명시되지 않음 | **.md 미러링 원칙** 명문화. raw .jsx/.html/.json 은 `10_RAW/` 보존, LLM이 핵심 정보를 `20_WIKI/`에 .md로 미러 |
| **Raw Reading Discipline** | 없음 | **MOS 사건 재발 방지**. 좌표(연도 × Item) 없이 raw 통째 Read 금지. 5종 소스 스키마 가이드(`20_WIKI/concepts/sources/`) 신설 |
| **Wiki 본질** | 종목 폴더 안 두꺼운 `synthesis.md` (분석 종합) | **분석 복제 금지**. per-asset `synthesis.md` 는 5~10줄 compounding 로그. 진짜 가치는 `concepts/`, `themes/`, `comparisons/` cross-cutting 페이지 |
| **Ingest 워크플로** | "소스 한 번 읽기 → 추출 → 갱신" | "좌표 통보만 받음 → raw 통째 Read 금지 → n개 페이지 propagation" — token economy 강제 |
| **Phase 3 산출물** | 종목 INDEX/synthesis 부트스트랩 + concept stub 5개 | + 소스 스키마 가이드 5종 (US/KR/JP × SEC/DART/EDINET/transcript) **신규 필수** |
| **Appendix A 루트 CLAUDE.md** | 6개 Rule | + "Raw Reading Discipline" 섹션 신규. 좌표 없으면 사용자 허가 필수 |

> v2.0.0 → v2.1.0 마이그레이션: v2.0.0 은 어떤 Phase도 시작되지 않은 상태이므로 v2.1.0 의 Phase 0 부터 그대로 시작 가능. v2.0.0 은 archive에 보존.

---

## 1. 이론적 토대 — LLM-Wiki 패턴이 왜 우리 문제를 푸는가

### 1.1 RAG vs Wiki — 결정적 차이

기존 NotebookLM/ChatGPT 업로드 방식은 **RAG(Retrieval-Augmented Generation)** 다:

> 질문 시점에 원자료에서 청크를 검색 → 매번 처음부터 합성. **누적이 없다.**

LLM-Wiki는 다르다:

> LLM이 원자료를 한 번 읽으면 **wiki에 영구 통합**한다 — 엔티티 페이지를 갱신하고, 모순을 표시하고, 종합문을 갱신한다. **wiki는 점점 풍부해지는 compounding artifact** 다.

**우리 케이스에 대입**:
- 현재 `S-anlyz/!Report/MSFT_분석대시보드.html`은 1회성 산출물. 다음 분기 분석 시 이전 인사이트가 자동으로 누적되지 않는다 → 매번 0에서 시작
- 채팅 기록은 `claude.ai`에 갇혀 있어 검색 불가 → 사고 흐름이 휘발됨
- archive `.md` 들은 단방향 텍스트 → 종목 간/시점 간 연결 없음

→ **각각의 산출물이 wiki 페이지로 압축·연결되고, 새 산출물 추가 시 관련 페이지가 함께 갱신**되어야 한다. 이게 v2의 핵심 전환점.

### 1.2 Wiki ≠ 분석의 복제 (v2.1.0 핵심 정정)

llm-wiki.md 원문을 다시 읽으면 wiki의 정의는 명확하다:

> *"updating entity pages, revising topic summaries, noting where new data **contradicts** old claims, strengthening or challenging the **evolving synthesis**"*

> *"Research: incrementally building a comprehensive wiki with an **evolving thesis**"*

**Wiki는 "MSFT 분석을 다시 쓰는 곳"이 아니라 "테제(thesis)가 진화하는 곳"이다.** 한 종목 분석 1건은 wiki 입장에서 데이터 포인트 1개일 뿐.

v2.0.0에서 종목 폴더 안에 두꺼운 `synthesis.md`(LLM 종합문)를 두려고 한 것은 분석 자체의 복제다 — 원본이 이미 `_artifacts/dashboard_<날짜>.html` 에 있는데 wiki에서 같은 내용을 다시 쓰는 건 무의미할 뿐 아니라 token 낭비다.

**Wiki가 해야 하는 일은 분석의 복제가 아니라**:
1. **Compounding** — 시간 누적. "이번 분석이 직전과 어떻게 달라졌나" Δ만 기록
2. **Entity 페이지** — PBR/Moat/Cyclical 같은 도메인 개념을 한 곳에 모은 페이지. 종목들은 이 페이지의 데이터 포인트
3. **Theme 페이지** — "AI capex 부담", "금리 사이클" 같은 cross-cutting 투자 테마
4. **Comparison 페이지** — MSFT vs GOOGL 클라우드 마진, 미국 vs 일본 종합상사
5. **Tag 검색** — frontmatter의 sector/theme/country 등으로 Dataview 동적 결합

→ §2~6에서 이를 폴더·운영으로 구현한다.

### 1.3 사용자와 LLM의 역할 분리

| 역할 | 사용자 | LLM (Claude Code) |
|---|---|---|
| 소스 큐레이션 | ★ | — |
| 좌표 통보 (어느 종목 어느 시점 어느 챕터) | ★ | — |
| 페이지 작성·갱신 | — | ★ |
| 종합·요약·교차참조 | — | ★ |
| 리스트 유지보수 (INDEX/LOG) | — | ★ |
| 깊이 사고·결정 | ★ | 보조 |
| **decisions.md 작성** | ★ | 참조만 |

**비개발자 친화의 핵심**: 사용자가 markdown/YAML/git 셋 다 직접 작성·관리하지 않는다. 모두 Claude Code 가 한다.

---

## 2. 3계층 아키텍처 — 폴더 prefix가 곧 Layer (v2.1.0 정정)

LLM-Wiki 원안의 3계층(Raw / Wiki / Schema)을 **물리적 폴더로 1:1 매핑**한다. v2.0.0의 추상 Layer 표기는 폐기.

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: Schema  (사람·LLM 합의서)                            │
│   └─ /CLAUDE.md  +  /_templates/                             │
└──────────────────────────────────────────────────────────────┘
            ↓ 규칙 정의
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: Wiki  (LLM 단독 작성·갱신, .md only, Obsidian 인덱싱) │
│   └─ /20_WIKI/                                                │
│       assets/ + concepts/ + themes/ + comparisons/ +         │
│       industry/ + macro/ + frameworks/ + plans/ +            │
│       methodology/ + screening/                              │
└──────────────────────────────────────────────────────────────┘
            ↑ "이 시점 그 분석"의 immutable 사실
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: Raw  (immutable, 다양한 포맷)                        │
│   └─ /10_RAW/                                                 │
│       assets/  (.jsx/.html/.json/.md 종목별 산출물)           │
│       screening/ (.html 카드 그리드)                          │
│       chats/    (.md export, 정착본)                         │
│       clippings/ (.md Web Clipper 결과)                      │
│       docs/    (.md 기존 plan/result/handoff)                │
│       attachments/ (이미지·PDF)                              │
│       inbox/   (분류 전 임시)                                 │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 계층별 운영 원칙 (강화판)

**Layer 1 — Raw (`10_RAW/`)**:
- LLM은 **수정하지 않는다**. 원본은 영구 보존
- `S-anlyz*/!Report/` JSX/HTML도 raw로 분류 (분석 파이프의 결정적 산출물 = "이 시점의 종목 사진"). 다시 만들 수 있어도 그 시점 그 분석은 immutable
- 채팅 raw export는 **gitignore** (개인정보 / 관리 파일 폭증 방지)
- **Raw Reading Discipline 적용**: 좌표 없이 통째 Read 금지 (§6.0)

**Layer 2 — Wiki (`20_WIKI/`)**:
- LLM이 **모든 페이지를 작성·갱신**한다
- **.md only** — Obsidian 그래프·검색·Dataview 의 작동 단위
- raw가 아닌 정보(.jsx/.html/.json)에 들어있는 핵심 사실은 LLM이 **.md로 미러링** (§2.3)
- 사용자의 메모는 `decisions.md` 또는 raw 의 `chats/`·`docs/` 에 별도 분리. wiki 본문은 LLM 단독
- 모든 페이지는 frontmatter 필수 (§5)
- 모든 갱신은 `LOG.md` 에 기록

**Layer 3 — Schema**:
- 볼트 루트 `CLAUDE.md` 는 **새로 작성** (wiki 운영 규칙 + Raw Reading Discipline)
- `S-anlyz*/CLAUDE.md` 와 `S-anlyz*/.claude/` 는 **건드리지 않는다** (분석 파이프 정책 = 별도 도메인)

### 2.2 폴더 prefix → 계층 식별 규칙

| Prefix | Layer | LLM 쓰기 가능? | 파일 포맷 |
|---|---|---|---|
| `10_*` | 1 (Raw) | ❌ (사용자 또는 외부 파이프라인이 떨어뜨림) | 자유 (.jsx/.html/.json/.md/.png/...) |
| `20_*` | 2 (Wiki) | ✅ | .md only |
| `90_*` | 1 (Archive Raw) | ❌ | 자유 |
| `_attachments/` | 1 (Asset Raw) | ❌ | 이미지/PDF |
| `_templates/` | 3 (Schema) | ✅ (스키마 변경 시) | .md |
| 루트 .md (CLAUDE/INDEX/LOG/MAP) | 2~3 | ✅ | .md |
| `S-anlyz*/` | 외부 도메인 | ❌ (이 플랜 범위 외) | — |

→ 폴더 번호만 보면 "여기 LLM이 글을 써도 되는가?"에 즉시 답이 나온다.

### 2.3 .md 미러링 원칙 (Obsidian 호환성 보장)

**문제**: Obsidian의 강점(그래프·백링크·검색·Dataview)은 `.md` 위에서만 작동한다. `.html`/`.jsx`/`.json` 은 그래프 노드로 들어가지 않는다.

**해결**: raw 원본은 `10_RAW/` 에 보존하고, **LLM이 핵심 정보를 .md로 추출해 `20_WIKI/`에 미러본을 만든다**.

| Raw 파일 (Layer 1) | LLM이 만드는 미러 (Layer 2) | Obsidian 동작 |
|---|---|---|
| `10_RAW/assets/US-MSFT/reports/dashboard_260503.jsx` | `20_WIKI/assets/US-MSFT/synthesis.md` 의 compounding 항목 1개 | .md 미러는 그래프 노드, .jsx 원본은 wikilink로 외부 앱 오픈 |
| `10_RAW/assets/US-MSFT/reports/dashboard_260503.html` | (위와 동일 미러 공유) | 동일 |
| `10_RAW/assets/US-MSFT/reports/SOURCE_PACKAGE_260503.json` | `20_WIKI/assets/US-MSFT/INDEX.md` 의 "Sources" 표 | URL 목록이 마크다운 표로 검색 가능 |
| `10_RAW/screening/20260503/US_스크리닝.html` | `20_WIKI/screening/260503_us-cyclical-themes.md` | 카드 그리드의 핵심 종목·테마만 .md로 추출 |
| `10_RAW/chats/claude/2026-04/raw.json` (gitignored) | `10_RAW/chats/claude/2026-04/_processed/<주제>.md` + 해당 종목 페이지 갱신 | LLM이 .json 분리 후 정착 |
| `10_RAW/clippings/<article>.md` (이미 .md) | 그대로 | wikilink로 직접 인용 가능 |

**원칙 (CLAUDE.md 루트에 명시)**:
> "Obsidian 그래프·검색에 들어가야 하는 정보는 LLM이 .md 미러를 만든다. 원본은 raw에 immutable artifact 로 둔다. 미러본에는 항상 원본 wikilink 를 포함한다."

---

## 3. 폴더 트리 (v2.1.0 정본)

```
!claudeProject/                          ← Obsidian 볼트 루트 (Layer 3 진입점)
│
├── CLAUDE.md                            ★ 볼트 스키마. 본 플랜 §1~6 압축본 + Raw Reading Discipline
├── INDEX.md                             ★ 콘텐츠 카탈로그. LLM이 ingest마다 갱신
├── LOG.md                               ★ 시간순 작업 로그. append-only
├── MAP.md                               사람용 네비게이션
│
├── 10_RAW/                              ★ Layer 1 통째로 — LLM 수정 금지
│   ├── assets/
│   │   └── <COUNTRY>-<TICKER>/          예: US-MSFT/, KR-005380/, JP-5401/
│   │       ├── reports/                 .jsx, .html, .json (S-anlyz 분석 산출물)
│   │       ├── chats/                   .md (Claude/Gemini export 정착본 — 종목 관련 부분만)
│   │       ├── clippings/               .md (Obsidian Web Clipper)
│   │       └── docs/                    .md (기존 plan*/result*/notebook prompt 이관본)
│   ├── screening/
│   │   └── <YYYYMMDD>/                  US/KR/JP 카드 그리드 .html, equity_ratios.json
│   ├── chats/
│   │   ├── claude/<YYYY-MM>/raw.json    (gitignored, 종목 미분류분)
│   │   ├── gemini/<YYYY-MM>/raw.json    (gitignored)
│   │   └── _processed/                  종목 분리 후 정착 대기
│   ├── clippings/                       종목 미분류 일반 자료 클리핑
│   ├── docs/                            archive `.md` 일반 (종목 미분류)
│   ├── attachments/                     이미지·PDF
│   └── inbox/                           분류 전 임시 영역
│
├── 20_WIKI/                             ★ Layer 2 통째로 — LLM 단독 작성, .md only
│   ├── assets/
│   │   └── <COUNTRY>-<TICKER>/
│   │       ├── INDEX.md                 ★ 종목 허브 — 메타·태그·raw 링크·테마 백링크
│   │       ├── synthesis.md             ★ compounding 로그 — 분석 1건당 5~10줄 Δ만
│   │       └── decisions.md             사용자 의사결정 (사용자 작성, LLM 참조만)
│   ├── concepts/                        ★ 도메인 개념 엔티티 페이지
│   │   ├── pbr.md
│   │   ├── economic-moat.md
│   │   ├── cyclical-investing.md
│   │   ├── fcf.md
│   │   ├── eps-quality.md
│   │   └── sources/                     ★ 신규: 소스 스키마 가이드 (Raw Reading 좌표 가이드)
│   │       ├── us-sec-10k-structure.md
│   │       ├── us-sec-10q-structure.md
│   │       ├── us-investing-transcript-structure.md
│   │       ├── kr-dart-yusil-structure.md
│   │       ├── jp-edinet-yuho-structure.md
│   │       └── source-package-schema.md
│   ├── themes/                          ★ 신규: cross-cutting 투자 테마
│   │   ├── ai-capex-burden.md
│   │   ├── rate-cycle-2026.md
│   │   └── shipping-supercycle.md
│   ├── comparisons/                     ★ 신규: 명시적 비교 분석
│   │   ├── msft-vs-googl-cloud-margin.md
│   │   └── us-vs-jp-trading-houses.md
│   ├── industry/                        업종 페이지
│   ├── macro/                           거시 환경
│   ├── frameworks/                      방법론 (jp-stock-analysis-framework, us-cyclical-screening 등)
│   ├── methodology/                     query 산출물 file-back 정착처
│   ├── screening/                       cross-screening 인사이트
│   └── plans/
│       ├── active/
│       └── done/
│
├── 90_ARCHIVE/                          은퇴 자료 (Layer 1 취급)
│   ├── handoffs/                        root HANDOFF-*.md 이관처
│   └── lint-reports/                    월간 lint 보고서
│
├── _templates/                          Templater 템플릿 (Schema 보조)
│   ├── asset-INDEX.md
│   ├── asset-synthesis.md
│   ├── concept.md
│   ├── theme.md
│   ├── comparison.md
│   ├── source-structure.md
│   ├── plan.md
│   └── chat-extract.md
│
├── S-anlyz/                             (기존 그대로, .claude 정책 유지 — Phase E에서만 다룸)
├── S-anlyz-kr/                          (기존 그대로)
├── S-anlyz-jp/                          (기존 그대로)
│
└── .obsidian/                           Obsidian 설정 (볼트 일부, Git 커밋)
```

### 3.1 v2.0.0 대비 폴더 변경점

| 변경 | 이유 |
|---|---|
| `10_ASSETS/` 폐기 → `10_RAW/assets/` + `20_WIKI/assets/` 분리 | Layer 1과 Layer 2를 한 폴더에 섞지 않음. 폴더 prefix가 곧 계층 |
| `_artifacts/` 표기 폐기 | underscore prefix 어색. `10_RAW/assets/<티커>/reports/` 자연스러움 |
| `20_SCREENING/` 폐기 → `10_RAW/screening/` + `20_WIKI/screening/` | 동일 원칙 |
| `00_INBOX/` 폐기 → `10_RAW/inbox/` + `10_RAW/chats/` | INBOX는 raw의 한 종류 |
| `30_FRAMEWORKS/` → `20_WIKI/frameworks/` | wiki 산하로 통합 |
| `40_PLANS/` → `20_WIKI/plans/` (active/done) | 동일 |
| `50_RESEARCH/concepts/` → `20_WIKI/concepts/` (+ `sources/` 신설) | 단순화 + 신규 가이드 |
| **`20_WIKI/concepts/sources/` 신설** | **Raw Reading Discipline 강제용**. 좌표 가이드 5+1종 |
| **`20_WIKI/themes/` 신설** | cross-cutting 테마. wiki의 진짜 가치 |
| **`20_WIKI/comparisons/` 신설** | 명시적 비교 분석 페이지 |
| `_attachments/` → `10_RAW/attachments/` | raw 산하로 일관 |

---

## 4. INDEX.md / LOG.md / MAP.md — 3대 메타파일

### 4.1 INDEX.md (콘텐츠 카탈로그)

**역할**: wiki 전체 페이지 + raw 자산 카탈로그. LLM이 ingest 시마다 갱신.

```markdown
---
type: index
updated: 2026-05-05
maintained_by: claude-code
---

# Vault Index

## Assets
| Asset | Country | Last Analyzed | Wiki | Raw |
|---|---|---|---|---|
| US-MSFT | US | 2026-05-03 | [[20_WIKI/assets/US-MSFT/INDEX]] | [[10_RAW/assets/US-MSFT]] |
| KR-005380 | KR | 2026-04-28 | [[20_WIKI/assets/KR-005380/INDEX]] | [[10_RAW/assets/KR-005380]] |

## Concepts (20_WIKI/concepts/)
- [[20_WIKI/concepts/pbr]] — PBR 해석 가이드
- [[20_WIKI/concepts/economic-moat]] — 경제적 해자 분석 프레임
- [[20_WIKI/concepts/sources/us-sec-10k-structure]] — US 10-K Item 구조 (Raw Reading 좌표용)

## Themes (20_WIKI/themes/)
- [[20_WIKI/themes/ai-capex-burden]] — AI capex 부담 사이클 (MSFT/GOOGL/AMZN/META)
- [[20_WIKI/themes/rate-cycle-2026]]

## Comparisons (20_WIKI/comparisons/)
- [[20_WIKI/comparisons/msft-vs-googl-cloud-margin]]

## Frameworks (20_WIKI/frameworks/)
...

## Recent Screening (20_WIKI/screening/)
...
```

**Claude의 진입 규칙**: 종목/주제 질문을 받으면 **반드시 INDEX.md 부터 읽고**, 거기서 발견한 페이지로 drill-down. 처음부터 raw grep 금지 (컨텍스트 폭발 방지).

### 4.2 LOG.md (시간순 append-only)

**역할**: ingest/query/lint 작업의 시간선.

```markdown
# Vault Log

## [2026-05-05 14:30] ingest | MSFT dashboard_260503
- Source: [[10_RAW/assets/US-MSFT/reports/dashboard_260503]] (LLM은 통째 Read하지 않음)
- Coordinates received from user: "Δ vs 직전 분석 — 클라우드 마진 +2.3%p, AI capex 18% 돌파"
- Updated:
  - [[20_WIKI/assets/US-MSFT/synthesis]] — compounding 항목 1개 append
  - [[20_WIKI/assets/US-MSFT/INDEX]] — Last Analyzed 갱신
  - [[20_WIKI/concepts/ai-capex-cycle]] — MSFT 데이터 포인트 갱신
  - [[20_WIKI/themes/ai-capex-burden]] — MSFT 사례 1줄 추가
  - [[20_WIKI/comparisons/hyperscaler-capex]] — MSFT 행 갱신

## [2026-05-05 10:15] query | "최근 30일 PBR<1 종목"
- Pages read: INDEX.md, 20_WIKI/assets/_index.md
- Raw consulted: none
- Result: 3 matches (KR-005380, JP-5401, US-MOS)
- Filed back: [[20_WIKI/methodology/pbr-screening-snapshot-260505]]

## [2026-05-04 18:00] lint
- Orphan pages: 1 (KR-088980 INDEX has no inbound links) → fixed
- Stale claims: 0
- Missing concept pages: cyclical-investing → created stub
- Raw reads detected without coordinates: 0 (clean)
```

**컨벤션**: `## [YYYY-MM-DD HH:MM] <op> | <subject>` 일관 prefix → 최근 활동 grep 가능.

### 4.3 MAP.md (사람용 진입점)

변경 빈도 낮음. 신입(미래의 자신)이 "이 볼트 어떻게 쓰는 곳?"에 5분 답을 얻는 곳.

---

## 5. Frontmatter 표준 (LLM 필터링 + Dataview 양립)

```yaml
---
type: asset-index | asset-synthesis | concept | theme | comparison | framework | plan | research | chat-extract | source-structure | handoff | log | index
asset: US-MSFT                 # 해당 종목 (없으면 생략)
country: US | KR | JP | global
date: 2026-05-05               # 작성/최종갱신
status: draft | active | done | archived | stable
sector: tech | financial | energy | ...           # GICS 11
tags: [valuation, cyclical, dividend]
themes: [ai-capex, rate-cycle]                    # ★ 신규: cross-cutting 테마 결합
concepts: [moat, fcf]                             # ★ 신규: 참조 concept 페이지
data_points: 4                                    # ★ 신규: 이 페이지가 종합한 분석 건수
source: claude-chat | gemini-chat | self | s-anlyz-pipeline | sec-filing | dart-filing | edinet-filing
related: ["[[20_WIKI/assets/US-MSFT/INDEX]]", "[[20_WIKI/concepts/economic-moat]]"]
mirrors_raw: "[[10_RAW/assets/US-MSFT/reports/dashboard_260503]]"   # ★ 미러본만. 원본 wikilink
last_lint: 2026-05-04          # lint 통과일 (해당 페이지만)
---
```

**`type` 어휘는 고정**. 새 type이 필요하면 `_templates/`에 새 템플릿 추가 + `CLAUDE.md` 의 type 목록 갱신을 한 커밋에 묶음.

**Dataview 활용 예시 (Phase 5)**:
```
TABLE asset, date, themes
FROM "20_WIKI/assets"
WHERE type = "asset-synthesis"
  AND contains(themes, "ai-capex")
SORT date DESC
```

---

## 6. 4대 오퍼레이션 — Reading Discipline / Ingest / Query / Lint

> v2.0.0 의 3대(Ingest/Query/Lint) 앞에 **§6.0 Raw Reading Discipline** 을 모든 오퍼레이션의 전제로 둔다. MOS 사건 재발 방지의 핵심.

### 6.0 Raw Reading Discipline (모든 오퍼레이션의 전제)

**원칙**: `10_RAW/` 의 .json/.html 파일은 **좌표(연도 × Item/섹션) 없이 통째로 Read 하지 않는다**.

**좌표가 정해지는 3가지 경로**:
1. **사용자 직접 통보**: "MSFT FY2025 10-K Item 7 MD&A 만 봐줘"
2. **분석 파이프 결과 메시지**: S-anlyz 산출물에 동봉된 "이번 분석의 핵심 Δ 3개"
3. **wiki에 이미 distilled** 되어 있어 raw read 불필요: `synthesis.md` 또는 `concepts/` 에서 충당

**좌표를 모를 때**: 먼저 `20_WIKI/concepts/sources/{country}-{type}-structure.md` 를 참조해 어느 Item에 무엇이 있는지 파악 후 후보 좌표 1~2개 결정. 그래도 모르면 **사용자에게 좌표를 요청**한다. 자유 탐색 raw read 절대 금지.

**위반 사례 (반복 금지)**:
- MOS 분석 시 21년 10-K 통째 Read → 컨텍스트 폭주, 시간·토큰 낭비
- supervisor의 수집 상한(7/6/6)은 ingest 단계 보호. 본 Discipline 은 **query/synthesis 단계 보호**. 두 보호막이 같이 있어야 재발하지 않음

**lint에서 검출**: `LOG.md` 항목에 raw read 가 좌표 없이 일어났는지 체크. 1건이라도 있으면 lint 실패.

### 6.1 Ingest (소스 통합)

**Trigger**: 사용자가 "이 자료 흡수해줘" 또는 분석 파이프가 새 산출물 생성.

**Workflow** (Claude Code가 따름):
1. 소스가 `10_RAW/` 의 어디에 안착했는지 확인 (raw 파일은 사용자/파이프가 떨어뜨림)
2. **사용자로부터 좌표 + Δ 3~5개 통보 받음** (또는 파이프 결과 메시지에서 추출)
3. raw 파일은 **통째로 Read 하지 않는다.** 좌표가 명시됐을 때만 해당 부분 핀포인트 Read
4. 갱신 대상 페이지 결정 (n개 propagation):
   - 종목이면: `20_WIKI/assets/<티커>/synthesis.md` 에 5~10줄 compounding 항목 append, `INDEX.md` 갱신
   - 개념 언급 시: `20_WIKI/concepts/<concept>.md` 갱신/생성
   - 테마 언급 시: `20_WIKI/themes/<theme>.md` 사례·데이터 포인트 1줄 추가
   - 비교 가능 시: `20_WIKI/comparisons/<comp>.md` 행 갱신
   - 모순 발견 시: 기존 페이지에 `> [!warning] Contradiction: ...` 콜아웃 추가
5. **`INDEX.md` 갱신** (새 페이지 추가 시)
6. **`LOG.md` append**: `## [YYYY-MM-DD HH:MM] ingest | <subject>` + 갱신 페이지 리스트 + raw read 좌표 (없으면 "none")
7. 사용자에게 변경 페이지 목록 제시 → 사용자 확인 → 커밋

**예시: MSFT 분석 dashboard_260503 ingest**:
```
입력: 10_RAW/assets/US-MSFT/reports/dashboard_260503.{jsx,html,json}
사용자 통보 Δ:
  - 클라우드 마진 +2.3%p (직전 +1.8%p)
  - AI capex/매출 18% 돌파
  - EPS guidance 하향 시작
LLM raw read: 없음 (Δ 통보로 충분)
영향:
  - 20_WIKI/assets/US-MSFT/synthesis.md  (compounding 항목 1개 append, 7줄)
  - 20_WIKI/assets/US-MSFT/INDEX.md      (Last Analyzed, mirrors_raw)
  - 20_WIKI/concepts/ai-capex-cycle.md   (MSFT 18% 임계 갱신)
  - 20_WIKI/themes/ai-capex-burden.md    (MSFT 사례 1줄)
  - 20_WIKI/comparisons/hyperscaler-capex.md (MSFT 행 갱신)
  - INDEX.md, LOG.md
Token: 분석 1건당 raw read 0회, wiki write n=6 페이지
```

### 6.2 Query (질문)

**Workflow**:
1. **항상 `INDEX.md` 부터 읽음** (raw grep 금지)
2. 후보 wiki 페이지 2~5개 식별 → 그것만 읽음
3. raw 가 필요하면 § 6.0 적용: 좌표 명시 후 핀포인트 Read
4. 답변 작성 + 출처 wiki링크 표시
5. **답변이 가치 있으면 wiki에 file-back**:
   - 비교/분석/연결 발견 → `20_WIKI/methodology/<주제>-<날짜>.md` 또는 `20_WIKI/comparisons/<주제>.md` 로 저장
   - LOG.md 에 query 기록

**금지**: 채팅 히스토리에만 남기고 끝내지 않는다. 가치 있는 발견은 반드시 wiki로 회수.

### 6.3 Lint (월 1회 건강검진)

**Trigger**: 사용자가 "lint" 또는 매월 1일 자동 (선택).

**체크 항목**:
| 검사 | 도구 |
|---|---|
| **좌표 없는 raw read 발생** | LOG.md grep — 발견 시 lint 실패 (§ 6.0 위반) |
| **synthesis.md 비대화** | 종목당 synthesis.md 가 항목당 평균 10줄 초과 → 분석 복제 의심 |
| 모순: 같은 사실에 대해 다른 페이지가 다른 주장 | LLM이 종목 synthesis 교차 read |
| Stale: 6개월 이상 갱신 없는 active 페이지 | frontmatter `date` + `status` |
| Orphan: inbound 링크 0개 페이지 | Obsidian graph view + grep `[[<page>]]` |
| 누락 개념: 본문에 자주 등장하나 concept 페이지 없음 | 빈도 분석 + concepts/ 디렉토리 차이 |
| 누락 테마/비교: 다수 종목 synthesis 가 같은 키워드 언급 | themes/ comparisons/ 후보 자동 제안 |
| 깨진 링크: `[[xxx]]` → 실제 파일 없음 | Obsidian 자체 기능 |
| Dead artifact: `10_RAW/`에 있으나 어떤 wiki 페이지도 mirror/참조 안 함 | grep |

**산출물**: `LOG.md` 에 `## [YYYY-MM-DD] lint` 항목 + `90_ARCHIVE/lint-reports/<날짜>.md` 상세 보고서.

---

## 7. 외부 채팅 Ingest 파이프라인

### 7.1 Claude.ai

1. 월 1회 Settings → Export data → JSON 다운로드
2. `10_RAW/chats/claude/<YYYY-MM>/raw.json` 저장 (gitignored)
3. Claude Code에 요청: *"이 raw.json을 종목/주제별 .md로 분리해줘. 각 .md 는 frontmatter `type: chat-extract, source: claude-chat` 부여"*
4. LLM이 `10_RAW/chats/_processed/` 에 분리 (이때 LLM은 raw.json 통째 read 가능 — chat 분리는 좌표 개념이 다름. 단 §6.0 정신에 따라 가능하면 사용자가 종목 키워드 list 선통보)
5. 사용자가 가치 있는 5~10개 선별 → Ingest 워크플로 (§6.1) 적용 → `10_RAW/assets/<티커>/chats/` 또는 `20_WIKI/methodology/` 로 정착
6. raw.json 은 gitignore. 가공된 .md만 커밋

### 7.2 Gemini

Google Takeout → 동일 파이프라인.

### 7.3 자동화 (선택, Phase 5 이후)

- PowerShell 폴더 감시 → `10_RAW/chats/.../raw.json` 들어오면 자동으로 Claude Code skill 호출
- Phase 5 안착 후 검토. v2.1.0 본문 범위 외.

---

## 8. 리스크 격리 마이그레이션 (Phase 0~5)

> 비개발자 멘탈 모델: **"위험한 작업 = ① 커밋 ② 새 브랜치 ③ 푸시 + 태그"**. Claude Code 가 명령어 만들고, 사용자는 승인만.

### Phase 0 — 안전망 (30분, 코드 변경 0)

- 현재 master `git status` M 다수 정리
  - 남길 변경 → 그대로 커밋 (`feat/pre-kb-v2.1-cleanup`)
  - 버릴 변경 → 사용자 명시 확인 (자동 폐기 절대 금지)
- 태그: `git tag v-pre-kb-v2.1`
- 푸시: `git push origin master --tags`
- 새 브랜치: `git checkout -b kb-v2.1/phase1-skeleton`

### Phase 1 — 골격 + 스키마 (2시간, 위험 0)

- **브랜치**: `kb-v2.1/phase1-skeleton`
- 작업:
  - `10_RAW/{assets,screening,chats,clippings,docs,attachments,inbox}/` 빈 폴더
  - `20_WIKI/{assets,concepts,themes,comparisons,industry,macro,frameworks,methodology,screening,plans/active,plans/done,concepts/sources}/` 빈 폴더
  - `90_ARCHIVE/{handoffs,lint-reports}/`, `_templates/`
  - `_templates/` 8종 템플릿 (asset-INDEX, asset-synthesis, concept, theme, comparison, source-structure, plan, chat-extract)
  - **루트 `CLAUDE.md` 작성** — 볼트 스키마 본문 (이 v2.1 플랜의 §1~6 압축본 + Raw Reading Discipline 명시)
  - 빈 `INDEX.md`, `LOG.md`, `MAP.md`
  - `.gitignore` 보강: `10_RAW/chats/**/raw.json`, `10_RAW/chats/**/raw/`
- 검증: Obsidian 으로 볼트 열기 → 폴더 진입, 템플릿 작동 확인. 루트 CLAUDE.md 에 §6.0 Raw Reading Discipline 포함 여부 확인
- 머지: master fast-forward → 태그 `v-kb-v2.1-phase1`

### Phase 2 — Layer 1 자산 이관 (4시간, 위험 중)

- **브랜치**: `kb-v2.1/phase2-migration`
- 작업:
  - `S-anlyz*/!Report/*.{jsx,html}` → `10_RAW/assets/<국가>-<티커>/reports/dashboard_<날짜>.{jsx,html}`
  - `S-anlyz*/raw/screening/*` → `10_RAW/screening/<YYYYMMDD>/`
  - `S-anlyz*/archive/*.md` → frontmatter 부여 후 `20_WIKI/plans/done/` 또는 `10_RAW/docs/` (사람작성 vs 결과물 구분)
  - root `HANDOFF-*.md` → `90_ARCHIVE/handoffs/`
  - `S-anlyz*/raw/<티커>/SOURCE_PACKAGE.json` 은 그대로 유지 + `10_RAW/assets/<티커>/reports/` 에 심볼릭 링크 또는 복사 (사용자 환경에 따라 결정)
- 세이프티:
  - **`git mv` 사용** (cp+rm 금지, 히스토리 보존)
  - **종목 1개당 1커밋** ("MSFT raw migration", "088980 raw migration")
  - 원본 폴더(`S-anlyz/!Report/`)는 **삭제하지 말고 유지** — 1주 병행 운영 후 검증되면 그때 제거 (별도 Phase 2-cleanup)
- 검증: 티커별 `10_RAW/assets/<티커>/reports/` 폴더 더블클릭 → JSX/HTML 열림. `git log --oneline` 종목 단위 식별 가능
- 머지: → 태그 `v-kb-v2.1-phase2`

### Phase 3 — Layer 2 부트스트랩 (4시간, **핵심**, 위험 낮음)

> v1에 없던 단계. LLM-Wiki 이론의 핵심 — **빈 폴더 ≠ wiki**. 초기 페이지가 있어야 compounding 시작.
> v2.0.0 대비 추가: **소스 스키마 가이드 5+1종 작성** 의무화 (Raw Reading Discipline 의 운영 전제)

- **브랜치**: `kb-v2.1/phase3-wiki-bootstrap`
- 작업 (전부 LLM 자동 + 사용자 검토):
  - **소스 스키마 가이드 작성 (먼저)**:
    - `20_WIKI/concepts/sources/us-sec-10k-structure.md` — Part I (Item 1/1A/1B/2/3) + Part II (Item 5/7/7A/8/9/9A) + III + IV. 각 Item에 무엇이 있는지 1줄 요약
    - `20_WIKI/concepts/sources/us-sec-10q-structure.md` — Part I (Item 1/2/3/4) + Part II (Item 1/1A/2/6)
    - `20_WIKI/concepts/sources/us-investing-transcript-structure.md` — Prepared Remarks/Q&A/Participants 위치, Investing/Motley/SA/ROIC 별 차이
    - `20_WIKI/concepts/sources/kr-dart-yusil-structure.md` — 사업의 내용/재무/이사회/주주/감사 등 한국 사업보고서 목차
    - `20_WIKI/concepts/sources/jp-edinet-yuho-structure.md` — 第一部 企業情報 (事業の状況/経理の状況) 등 일본 有価証券報告書 목차
    - `20_WIKI/concepts/sources/source-package-schema.md` — 우리 시스템 내부 SOURCE_PACKAGE.json 구조 + sec_10k[]/sec_10q[]/transcripts[] 키 의미
  - **종목별 INDEX.md 자동 생성** (`10_RAW/assets/<티커>/` 메타 + SOURCE_PACKAGE.json 의 URL 표 미러 + raw 링크)
  - **종목별 synthesis.md 부트스트랩** — 가장 최근 dashboard 산출물에서 **5~10줄만 추출** (분석 복제 절대 금지). 사용자가 직접 Δ 통보하지 않은 경우 stub 으로 시작 (`## [YYYY-MM-DD] bootstrap | source: dashboard_<날짜>` 한 줄)
  - 루트 `INDEX.md` 채우기 — 모든 종목 + 기존 framework + 기존 plan 카탈로그
  - `LOG.md` 부트스트랩 항목 추가
  - `20_WIKI/concepts/` stub 페이지 6개 (PBR / Cyclical / Moat / FCF / EPS quality / AI capex cycle)
  - `20_WIKI/themes/` stub 페이지 2~3개 (현재 운영 중인 테마)
- 사용자 검토: 종목당 30초씩 훑어보고 "오류 / 사실관계" 만 표시. 글 다듬기는 LLM
- 머지: → 태그 `v-kb-v2.1-phase3`

### Phase 4 — 외부 채팅 1차 흡입 (2시간, 위험 낮음)

- **브랜치**: `kb-v2.1/phase4-chats`
- §7 파이프라인 1회 실행: Claude.ai + Gemini 1개월 분 export
- 가공 .md 5~10개 → 종목/연구 폴더로 정착 (Ingest 워크플로 적용)
- 머지: → 태그 `v-kb-v2.1-phase4`

### Phase 5 — 운영 안착 (3시간, 위험 0)

- **브랜치**: `kb-v2.1/phase5-ops`
- Obsidian Dataview 플러그인 설치 → `INDEX.md` 동적화 (수동 표 → frontmatter 기반 자동 표). themes/concepts 결합 쿼리 1개 검증
- `MAP.md` 보강 (사람용 5분 가이드)
- **첫 lint 실행** (§6.3) → orphan / stale / missing concept / **좌표 없는 raw read 0건** 보고서
- 루트 `CLAUDE.md` 최종 확정 (Phase 1 작성 + Phase 2~4 운영 경험 반영)
- 머지: → 태그 `v-kb-v2.1-stable`

---

## 9. Phase E (별도, 본 v2.1 범위 외) — 3국 `.claude` 통합

> **사용자 결정**: 본 v2.1.0 에서는 다루지 않는다. 폴더는 `S-anlyz/`, `S-anlyz-kr/`, `S-anlyz-jp/` 그대로 유지.

이 §는 v2.1 운영이 안정된 뒤 별도 플랜에서 다루기 위한 **인터페이스 정의**만 둔다.

### 9.1 인터페이스 (v2.1이 보장하는 것)

- 볼트 루트 `CLAUDE.md` 는 `S-anlyz*/CLAUDE.md` 와 **이름·역할 분리**된 도메인. v2.1 어떤 단계에서도 분석 파이프 CLAUDE.md를 수정하지 않는다
- `60_AGENTS/` 폴더 **금지**. 추후 통합 작업은 별도 폴더(예: 미래의 `60_PIPELINE/`) 또는 별도 저장소에서 진행
- v2.1 운영 중 발견되는 3국 차이는 `LOG.md` 에 `## [YYYY-MM-DD] observation | agent-diff: ...` 형식으로 누적

### 9.2 Phase E 진입 트리거 (참고용, 본 플랜 외)

- v2.1 Phase 5 안착 후 최소 **2주 운영 관찰**
- A/B 비교 검증 (시범 국가 1개 → 1주 분석 결과 동등성 확인)
- 자세한 절차는 `PLAN_통합지식관리-리스크격리_260504.md` §Phase E 참조

---

## 10. 사고 시 복구 (비개발자 직접 가능)

| 사고 | 복구 명령 (Claude Code 가 만들어주고 사용자는 승인만) |
|---|---|
| "이번 phase 처음부터" | `git reset --hard <태그>` (예: `v-kb-v2.1-phase1`) |
| "방금 파일 이동만 무효화" | `git revert <commit-hash>` |
| "브랜치 통째로 폐기" | `git checkout master && git branch -D kb-v2.1/<branch>` |
| "PC 망가짐" | 다른 PC `git clone <원격URL>` → 마지막 푸시까지 복구 |
| "wiki 페이지 LLM이 잘못 갱신" | 해당 파일만 `git checkout HEAD~1 -- <path>` 후 재작성 의뢰 |
| "Phase E(미래) 통합 후 분석 회귀" | `git checkout master` 1줄 — Phase E 브랜치 무효화 |
| "synthesis.md 가 분석 복제처럼 비대해짐" | lint 1회 → 비대 페이지 식별 → 해당 부분 트리밍 + concepts/themes 로 분산 재배치 |

---

## 11. 검증 체크리스트 (Phase별 통과 기준)

| Phase | 통과 기준 |
|---|---|
| 0 | `git tag` 에 `v-pre-kb-v2.1`, 원격 `master`/`tags` 동기화 |
| 1 | Obsidian 볼트로 열림 / `10_*` `20_*` `90_*` 폴더 진입 가능 / 루트 `CLAUDE.md` 에 **§6.0 Raw Reading Discipline 포함** / 템플릿 8종 작동 |
| 2 | 모든 종목 `10_RAW/assets/<티커>/reports/` 더블클릭 정상, `git log --oneline` 종목 단위 커밋 식별, 원본 `S-anlyz*/!Report/` 보존 |
| 3 | **소스 스키마 가이드 6종 작성 완료** / 모든 종목 `20_WIKI/assets/<티커>/INDEX.md` + `synthesis.md` 존재 (synthesis는 stub 또는 5~10줄) / 루트 `INDEX.md` 카탈로그 완성 / `LOG.md` 부트스트랩 항목 / **분석 복제 0건** |
| 4 | `10_RAW/chats/.../raw.json` 존재(미커밋), 가공된 `.md` 5+ 정착, `LOG.md` ingest 항목, **각 ingest 항목의 raw read 좌표 기록 또는 "none"** |
| 5 | Dataview 동적 표 1개 작동 (themes/concepts 결합 쿼리 포함), 첫 lint 보고서 1건, **좌표 없는 raw read 0건**, `MAP.md` 5분 가이드, 루트 `CLAUDE.md` 운영 규칙 확정 |

---

## 12. 즉시 실행 가능한 첫 액션

1. **A안 (보수적)**: Phase 0 + Phase 1만 — 안전망 + 골격. 기존 자산 무수정. 약 2.5h
2. **B안 (중간, 권장)**: Phase 0~3 — 안전망 + 골격 + 자산 이관 + **wiki 부트스트랩 + 소스 스키마 가이드**. wiki가 "빈 그릇 → 살아있는 시스템"이 되는 지점까지. 약 11h, Claude Code 8할 수행
3. **C안 (적극)**: Phase 0~5 일괄 — 채팅 흡입 + 운영 안착까지. 약 16h. 시범 종목 1개로 검증 후 권장

비개발자 + Auto mode 환경에서는 **B안 (Phase 3까지)** 권장. wiki 부트스트랩 + 소스 스키마 가이드까지 가야 LLM-Wiki 패턴의 가치 + Raw Reading Discipline 의 보호막이 같이 작동한다. 채팅 흡입(Phase 4)과 운영(Phase 5)은 한 주 띄워도 무방.

---

## 13. 향후 확장 (v2.1 안착 후 검토)

### 13.1 검색 인프라 (qmd CLI)

볼트 페이지 100개 초과 시: [qmd](https://github.com/tobi/qmd) 도입 검토 — BM25+벡터 하이브리드 + LLM 재랭킹, on-device. CLI/MCP 양쪽 지원.

### 13.2 Marp 슬라이드 출력

Obsidian Marp 플러그인. wiki 페이지 → 발표 자료 즉시 변환. 종목 분석 요약, 분기 리뷰에 활용.

### 13.3 Supabase (3차 색인)

종목 50개 초과 + 정형 쿼리 니즈 ("ROE>15 ∩ PER<15 전체 종목") 발생 시. Obsidian frontmatter → Supabase row 자동 upsert (Claude Code skill).

### 13.4 Phase E (`.claude` 통합)

§9 참조. v2.1 안착 후 별도 플랜에서.

### 13.5 Raw 자동 좌표 추출 (token 절약 강화)

ingest 시 사용자 통보 Δ 가 부족해도, raw 파일의 **목차/소제목/Item 헤더만 한 번 스캔**해 좌표 후보 자동 제안. 본문 통째 읽기 없이 좌표만 추출. Phase 5 이후.

---

## 부록 A — 루트 `CLAUDE.md` 골격 (Phase 1 작성 대상, v2.1 정본)

볼트 루트에 둘 스키마 문서. 본 플랜 §1~6 의 운영 규칙 압축본 + Claude Code 가 따를 명령형 룰.

```markdown
# Vault CLAUDE.md (LLM-Wiki Schema v2.1)

This vault is an LLM-maintained knowledge base. You are the maintainer.

## Folder ↔ Layer Mapping (BINDING)
- `10_*` and `90_*` and `_attachments` and `S-anlyz*/`  → Layer 1 (Raw). NEVER modify.
- `20_*` and root `INDEX.md`/`LOG.md`/`MAP.md`  → Layer 2 (Wiki). LLM writes here only. .md only.
- `/CLAUDE.md` and `_templates/`  → Layer 3 (Schema).

## Rules
1. NEVER modify Layer 1 raw (`10_RAW/`, `90_ARCHIVE/`, `_attachments/`, `S-anlyz*/raw/`, `S-anlyz*/!Report/`, `10_RAW/chats/.../raw.json`).
2. NEVER modify `S-anlyz*/CLAUDE.md` or `S-anlyz*/.claude/` — separate domain.
3. ALWAYS read `INDEX.md` first when receiving asset/topic queries. Never grep `10_RAW/` blindly.
4. ALWAYS append to `LOG.md` after ingest/query/lint with `## [YYYY-MM-DD HH:MM] <op> | <subject>` prefix.
5. ALWAYS ensure frontmatter on every .md you write/update.
6. NEVER skip cross-reference updates: an ingest must touch `INDEX.md` + `LOG.md` + at least 1 entity/concept/theme/comparison page besides the asset folder.
7. NEVER duplicate the analysis content in wiki. `synthesis.md` per asset = compounding log only (5~10 lines per analysis, Δ vs prior). The full analysis lives in `10_RAW/assets/<TICKER>/reports/`.

## Raw Reading Discipline (MOS Lesson — BINDING)
1. NEVER Read a `.json` or `.html` file in `10_RAW/` in full. Always have coordinates first.
2. Coordinates = (asset, fiscal year, Item/section). Examples:
   - "MSFT FY2025 10-K Item 7 MD&A"
   - "005380 2024 사업보고서 재무에 관한 사항"
   - "Q3 2025 earnings call transcript Q&A section only"
3. If coordinates are not provided by user or pipeline message, FIRST consult `20_WIKI/concepts/sources/{country}-{type}-structure.md` to identify candidate Item(s).
4. If still unclear, ASK the user for coordinates. Free exploration full-read is FORBIDDEN.
5. The supervisor's source collection cap (7 10-K, 6 10-Q, 6 transcripts) protects ingest. This Discipline protects query/synthesis. Both layers must hold.
6. Every ingest's LOG.md entry must record raw read coordinates or "none". Lint will fail otherwise.

## Mirror Principle (Obsidian Compatibility)
1. Information that should appear in Obsidian graph/search/Dataview must exist as `.md` in `20_WIKI/`.
2. Raw `.jsx`/`.html`/`.json` stays as immutable artifact in `10_RAW/`.
3. Every wiki .md derived from a raw artifact must include `mirrors_raw: "[[10_RAW/...]]"` in frontmatter.

## Workflows
- Reading Discipline: see PLAN v2.1.0 §6.0
- Ingest: see PLAN v2.1.0 §6.1
- Query: see PLAN v2.1.0 §6.2
- Lint: see PLAN v2.1.0 §6.3

## Frontmatter Vocabulary
type ∈ {asset-index, asset-synthesis, concept, theme, comparison, framework, plan, research, chat-extract, source-structure, handoff, log, index}
```

---

## 부록 B — Obsidian 추천 플러그인 (모두 무료)

| 플러그인 | 용도 | v2.1 필수도 |
|---|---|---|
| Dataview | frontmatter 기반 동적 표 (themes/concepts 결합 쿼리) | ★★★ (Phase 5) |
| Templater | 노트 생성 시 frontmatter 자동 채움 | ★★★ (Phase 1) |
| Tag Wrangler | 태그 통합 관리 | ★★ |
| Excalidraw | 손그림/다이어그램 | ★ |
| Git | 볼트 백업 (CLI git 사용 중이면 선택) | ★★ |
| Marp | 슬라이드 출력 | ★ (확장) |

---

## 부록 C — 네이밍 규칙 표준

- 종목 폴더: `<국가>-<티커>` (예: `US-MSFT`, `KR-005380`, `JP-5401`)
- 종목 산출물 (raw): `10_RAW/assets/<티커>/reports/dashboard_<YYMMDD>.{jsx,html}`
- 종목 SOURCE_PACKAGE: `10_RAW/assets/<티커>/reports/SOURCE_PACKAGE_<YYMMDD>.json`
- 스크리닝 산출물 (raw): `10_RAW/screening/<YYYYMMDD>/<COUNTRY>_스크리닝.html`
- 종목 wiki: `20_WIKI/assets/<국가>-<티커>/{INDEX,synthesis,decisions}.md`
- 개념: `20_WIKI/concepts/<concept-kebab>.md`
- 소스 스키마: `20_WIKI/concepts/sources/<country>-<type>-structure.md`
- 테마: `20_WIKI/themes/<theme-kebab>.md`
- 비교: `20_WIKI/comparisons/<a>-vs-<b>.md`
- 플랜: `20_WIKI/plans/active|done/PLAN_<주제>_<YYMMDD>.md`, 버전 시 `_v<MAJOR.MINOR.PATCH>`
- 결과: `20_WIKI/methodology/RESULT_<주제>_<YYMMDD>.md`
- Lint 보고서: `90_ARCHIVE/lint-reports/lint-report-<YYMMDD>.md`
- 분석 노트: `10_RAW/assets/<티커>/chats/<YYYY-MM-DD>_<주제>.md`
- 채팅 발췌: `10_RAW/chats/_processed/<source>_<YYYY-MM>_<주제>.md`
- Git 태그: `v-kb-v2.1-<phase>`, `v-kb-v2.1-stable`
- Git 브랜치: `kb-v2.1/<phase-name>`

---

## 부록 D — v2.0.0 → v2.1.0 마이그레이션

본 v2.1.0 은 v2.0.0 을 **전면 대체**한다. v2.0.0 `PLAN_통합지식관리체계_v2.0.0_260504.md` 는 archive에 그대로 보존하되, 신규 작업은 v2.1 기준으로 진행한다.

v2.0.0 → v2.1.0 마이그레이션 경로:
- v2.0.0 어떤 Phase도 시작되지 않은 상태이므로, v2.1.0 Phase 0 부터 그대로 시작 가능.
- 만약 v2.0.0 Phase 1 작업이 진행됐다면:
  - `00_INBOX/` → `10_RAW/inbox/` + `10_RAW/chats/` 로 분할 이동
  - `10_ASSETS/<티커>/_artifacts/` → `10_RAW/assets/<티커>/reports/` 로 이동
  - `10_ASSETS/<티커>/synthesis.md` → `20_WIKI/assets/<티커>/synthesis.md` 로 이동 후 분석 복제분 트리밍 (5~10줄 compounding 로그로 축소)
  - `30_FRAMEWORKS/`, `40_PLANS/`, `50_RESEARCH/concepts/` → `20_WIKI/` 산하로 이동
  - `_attachments/` → `10_RAW/attachments/` 이동
  - 루트 `CLAUDE.md` 갱신 (§6.0 Raw Reading Discipline + Mirror Principle 추가)
- v2.0.0 Phase 2 까지 진행됐다면 위에 더해 `_artifacts/` 폴더 통째 `10_RAW/assets/<티커>/reports/` 로 git mv.

---

## 부록 E — Source Schema Guide 작성 가이드 (Phase 3 산출물)

각 가이드는 다음 표준 구조를 따른다 (`_templates/source-structure.md` 템플릿 사용).

```markdown
---
type: source-structure
country: US | KR | JP
source: sec-10k | sec-10q | investing-transcript | dart-yusil | edinet-yuho | source-package
date: 2026-05-05
status: stable
---

# {Source Name} 구조 가이드

## 목적
이 가이드는 LLM이 {source} 파일을 읽기 전에 좌표(연도 × Item)를 정하기 위한 참조 문서다.
Raw Reading Discipline (CLAUDE.md §Raw Reading Discipline) 의 운영 전제.

## 파일 형태
- 포맷: HTML | JSON | PDF
- 일반 위치: `10_RAW/assets/<티커>/reports/...` 또는 외부 URL
- 평균 토큰 규모: ~~k tokens (통째 read 시 컨텍스트 폭주 위험)

## 섹션·Item 구조
| Item/섹션 | 내용 1줄 요약 | 우리 분석에서 자주 쓰는 용도 |
|---|---|---|
| Part I Item 1 Business | 사업 개요 | 첫 분석 시 사업 모델 파악 |
| Part I Item 1A Risk Factors | 리스크 팩터 | strategy-risk-agent 의 risk_findings |
| Part II Item 7 MD&A | 경영진 분석 | performance-agent 의 financial_findings |
| ... | ... | ... |

## 좌표 통보 형식 예시
- "MSFT FY2025 10-K Item 7 MD&A"
- "MSFT FY2025 10-K Item 1A Risk Factors only"

## 관련 Concept/Theme 백링크
- [[20_WIKI/concepts/economic-moat]]
- [[20_WIKI/themes/ai-capex-burden]]
```

각 가이드 분량은 1~2 페이지 정도면 충분. **본문 인용은 금지** (저작권 + 변동성). 구조와 좌표 어휘만 정리.
