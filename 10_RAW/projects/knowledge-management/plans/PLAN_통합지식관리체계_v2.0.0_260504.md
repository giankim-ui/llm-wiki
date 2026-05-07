---
title: 통합 투자 지식 관리 체계 v2.0.0
date: 2026-05-04
tags: [plan, knowledge-management, investment, obsidian, v2.0.0]
---

# PLAN — 통합 투자 지식 관리 체계 v2.0.0

- **작성일**: 2026-05-04
- **이전 버전**: `PLAN_통합지식관리체계_260504.md` (v1.0), `PLAN_통합지식관리-리스크격리_260504.md` (v1.0 보완)
- **반영 이론**: `llm-wiki.md` (LLM-as-wiki-maintainer 패턴)
- **대상 자산**: AI 채팅 기록(Claude/Gemini) + JSX/HTML 결과물(국가별) + archive 마크다운 + 캡처/스터디 자료
- **목표**: 흩어진 자료를 **"compounding 가능한 단일 지식 베이스"** 로 통합 — 사용자는 사고하고, LLM은 유지보수한다

---

## 0. v2.0.0 변경 요약 (v1 대비)

| 영역 | v1 | v2.0.0 |
|---|---|---|
| **이론 기반** | Obsidian + frontmatter (도구 중심) | **LLM-Wiki 3계층 모델** (Raw / Wiki / Schema) — 도구는 결과물 |
| **핵심 메타파일** | `MAP.md` 1개 | **`INDEX.md` + `LOG.md` + `MAP.md`** — 카탈로그·시간선·사람용 진입점 분리 |
| **워크플로** | 마이그레이션 + Dataview만 | **Ingest / Query / Lint** 3대 오퍼레이션 명문화 |
| **`60_AGENTS/` 폴더** | 포함 (3국 .claude 통합) | **제거**. `.claude/` 정책과 위배 → 기존 국가별 폴더 유지 |
| **3국 `.claude` 통합** | Week 4 작업으로 포함 | **본 플랜 범위 외**. 별도 Phase E로 후행, v2 본문에서는 인터페이스만 정의 |
| **마이그 안전장치** | 4주 plan | **Phase 0~5 브랜치/태그/롤백 체크리스트** (리스크 격리 v1 반영) |
| **종목 폴더 내부** | `INDEX.md` + dashboard + notes/ + data/ | **`INDEX.md`(허브) + `synthesis.md`(LLM 종합) + `_artifacts/`(immutable) + `_notes/`(사람·채팅 발췌)** — 계층 구분 명확 |
| **개념 페이지** | 없음 | **`50_RESEARCH/concepts/`** — PBR/Cyclical/Moat 등 도메인 개념 wiki 페이지 도입 |
| **자동화 운영** | 수동 export 권장 | **Ingest/Lint 워크플로 정의 + 월 1회 lint 의무화** |

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

→ **각각의 산출물이 wiki 페이지 하나로 통합되고, 새 산출물 추가 시 관련 페이지가 함께 갱신**되어야 한다. 이게 v2의 핵심 전환점.

### 1.2 사용자와 LLM의 역할 분리

| 역할 | 사용자 | LLM (Claude Code) |
|---|---|---|
| 소스 큐레이션 | ★ | — |
| 좋은 질문 | ★ | — |
| 의사결정 | ★ | — |
| **요약/교차참조/일관성 유지/북킹** | — | ★ |
| **wiki 페이지 작성·갱신** | — | ★ |
| 그래프뷰·검색·읽기 | ★ | ★ (조회) |

**원칙**: *"You read it; the LLM writes it."* 사용자는 wiki를 거의 직접 쓰지 않는다.

---

## 2. 3계층 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3: SCHEMA (사용자 ↔ LLM 협업 규칙)                  │
│  - C:/Users/nayut/!claudeProject/CLAUDE.md  ← 볼트 루트    │
│  - S-anlyz*/CLAUDE.md                       ← 분석 파이프 │
│  - S-anlyz*/.claude/                        ← 에이전트(불변)│
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ 규칙 적용
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: WIKI (LLM이 쓰고 유지)                          │
│  - INDEX.md, LOG.md, MAP.md                              │
│  - 10_ASSETS/<티커>/INDEX.md, synthesis.md               │
│  - 50_RESEARCH/concepts/*.md  (엔티티/개념 페이지)        │
│  - 20_SCREENING/synthesis/*.md                           │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Ingest (LLM이 읽고 wiki에 통합)
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: RAW (불변 원천 — LLM은 읽기만)                  │
│  - S-anlyz*/raw/  (SEC 10-K/Q, transcripts)              │
│  - S-anlyz*/!Report/*.{jsx,html}  (분석 파이프 산출물)    │
│  - 00_INBOX/chats/.../raw.json  (Claude/Gemini export)   │
│  - _attachments/  (캡처·이미지·PDF)                       │
└─────────────────────────────────────────────────────────┘
```

### 2.1 계층별 운영 원칙

**Layer 1 — Raw**:
- LLM은 **수정하지 않는다**. 원본은 영구 보존
- `S-anlyz*/!Report/` JSX/HTML도 raw로 분류 (분석 파이프의 결정적 산출물 = "이 시점의 종목 사진"). 다시 만들 수 있어도 그 시점 그 분석은 immutable
- 채팅 raw export는 **gitignore** (개인정보 / 관리 파일 폭증 방지)

**Layer 2 — Wiki**:
- LLM이 **모든 페이지를 작성·갱신**한다
- 사용자의 메모는 `_notes/` 에 별도 분리 (LLM은 참조만)
- 모든 페이지는 frontmatter 필수 (§5)
- 모든 갱신은 `LOG.md` 에 기록

**Layer 3 — Schema**:
- 볼트 루트 `CLAUDE.md` 는 **새로 작성** (wiki 운영 규칙)
- `S-anlyz*/CLAUDE.md` 와 `S-anlyz*/.claude/` 는 **건드리지 않는다** (분석 파이프 정책 = 별도 도메인)

---

## 3. 폴더 트리 (단일 볼트, 60_AGENTS 제거)

```
!claudeProject/                          ← Obsidian 볼트 루트, Layer 3 진입점
│
├── CLAUDE.md                            ★ 볼트 스키마. wiki 운영 규칙·Ingest/Query/Lint 워크플로
├── INDEX.md                             ★ 콘텐츠 카탈로그. LLM이 ingest마다 갱신
├── LOG.md                               ★ 시간순 작업 로그. append-only. ingest/query/lint 모두 기록
├── MAP.md                               사람용 네비게이션 (변경 빈도 낮음)
│
├── 00_INBOX/                            Layer 1·2 사이의 임시 영역
│   ├── chats/
│   │   ├── claude/YYYY-MM/raw.json      (gitignored)
│   │   ├── gemini/YYYY-MM/raw.json      (gitignored)
│   │   └── _processed/                  종목별 분리 후 정착 대기
│   └── captures/                        자료실/스크린샷 임시 대기
│
├── 10_ASSETS/                           ★ Layer 2 핵심: 종목 단위 통합 (국가 무관)
│   ├── _index.md                        모든 종목 카탈로그 (Dataview 동적 표 권장)
│   ├── US-MSFT/
│   │   ├── INDEX.md                     ★ 종목 허브 (LLM 작성). Claude 진입점
│   │   ├── synthesis.md                 ★ LLM 종합문. 새 분석마다 갱신 (compounding)
│   │   ├── decisions.md                 사용자 의사결정 로그 (사용자 작성)
│   │   ├── _artifacts/                  Layer 1: 산출물 (immutable, 날짜 suffix)
│   │   │   ├── dashboard_260503.jsx
│   │   │   ├── dashboard_260503.html
│   │   │   └── source-package_260503.json
│   │   └── _notes/                      Layer 2: 자유 메모·채팅 발췌
│   ├── KR-005380/
│   ├── JP-5401/
│   └── ...
│
├── 20_SCREENING/                        스크리닝 산출물 + 종합
│   ├── _index.md
│   ├── _artifacts/                      Layer 1: 날짜별 원본 HTML
│   │   ├── US_20260503.html
│   │   ├── KR_20260502.html
│   │   └── JP_20260430.html
│   └── synthesis/                       Layer 2: LLM이 추출한 cross-screening 인사이트
│       └── 260503_us-cyclical-themes.md
│
├── 30_FRAMEWORKS/                       분석 방법론 (사람·LLM 공저)
│   ├── _index.md
│   ├── jp-stock-analysis-framework.md
│   ├── us-cyclical-screening.md
│   └── industry/
│
├── 40_PLANS/                            작업 계획·결과 문서
│   ├── _index.md
│   ├── active/
│   └── done/                            완료 시 frontmatter status:done + 이동
│
├── 50_RESEARCH/                         ★ Layer 2: 도메인 wiki (엔티티·개념 페이지)
│   ├── _index.md
│   ├── concepts/                        ★ 신규: 개념 페이지 (PBR/Cyclical/Moat/...)
│   │   ├── pbr.md
│   │   ├── cyclical-investing.md
│   │   └── economic-moat.md
│   ├── macro/                           거시 환경 페이지
│   ├── industry/                        업종 페이지
│   └── methodology/
│
├── 70_STUDIES/                          개인 학습 자료
│
├── 90_ARCHIVE/                          은퇴 자료
│   └── handoffs/                        root HANDOFF-*.md 이관처
│
├── _attachments/                        Layer 1: 이미지/PDF
├── _templates/                          Templater 템플릿
│   ├── asset-INDEX.md
│   ├── asset-synthesis.md
│   ├── concept.md
│   ├── plan.md
│   └── chat-extract.md
│
├── S-anlyz/                             (기존 그대로, .claude 정책 유지)
├── S-anlyz-kr/                          (기존 그대로)
├── S-anlyz-jp/                          (기존 그대로)
│
└── .obsidian/                           Obsidian 설정 (볼트 일부, Git 커밋)
```

### 3.1 v1 대비 폴더 변경점

| 변경 | 이유 |
|---|---|
| `60_AGENTS/` **제거** | `.claude/` 정책 위배. 3국 `.claude` 통합은 Phase E로 후행 (§9) |
| `S-anlyz*/` 그대로 유지 | 분석 파이프 + `.claude` 영역은 Layer 3 별도 도메인. 볼트가 이를 *포함* 하되 *간섭하지 않음* |
| `_artifacts/` 도입 (종목/스크리닝) | Layer 1과 Layer 2 시각적 분리. immutable 원본은 `_` prefix |
| `synthesis.md` (종목) | LLM의 compounding 결과물. 분석 추가 시마다 LLM이 갱신 |
| `decisions.md` (종목) | 사용자가 직접 쓰는 의사결정 로그. LLM은 참조만 |
| `50_RESEARCH/concepts/` | 도메인 개념별 wiki 페이지. Tolkien Gateway 식 엔티티 페이지 |
| 루트 `INDEX.md` + `LOG.md` | LLM-Wiki 표준. MAP.md(사람용)와 역할 분리 |
| 루트 `CLAUDE.md` | 볼트 스키마. 분석 파이프 `S-anlyz*/CLAUDE.md` 와 다른 도메인 |

---

## 4. INDEX.md / LOG.md / MAP.md — 3대 메타파일

### 4.1 INDEX.md (콘텐츠 카탈로그)

**역할**: wiki 전체 페이지 목록. LLM이 ingest 시마다 갱신.

```markdown
---
type: index
updated: 2026-05-04
maintained_by: claude-code
---

# Vault Index

## Assets (10_ASSETS/)
| Asset | Country | Last Analyzed | Synthesis | Tags |
|---|---|---|---|---|
| [[10_ASSETS/US-MSFT/INDEX]] | US | 2026-05-03 | [[10_ASSETS/US-MSFT/synthesis]] | tech, moat |
| [[10_ASSETS/KR-005380]] | KR | 2026-04-28 | ... | cyclical, auto |
...

## Concepts (50_RESEARCH/concepts/)
- [[50_RESEARCH/concepts/pbr]] — Price-to-Book Ratio 해석 가이드
- [[50_RESEARCH/concepts/cyclical-investing]] — 시클리컬 투자 프레임워크
...

## Frameworks (30_FRAMEWORKS/)
...

## Recent Screening (20_SCREENING/)
...
```

**Claude의 진입 규칙**: 종목/주제 질문을 받으면 **반드시 INDEX.md 부터 읽고**, 거기서 발견한 페이지로 drill-down. 처음부터 종목 폴더 grep 금지 (컨텍스트 폭발 방지).

### 4.2 LOG.md (시간순 append-only)

**역할**: ingest/query/lint 작업의 시간선. 사람도 LLM도 "최근 무슨 일이 있었나"를 빨리 안다.

```markdown
# Vault Log

## [2026-05-04 14:30] ingest | MSFT 10-K FY2025
- Source: S-anlyz/raw/MSFT/sources/sec_10k/FY2025_xxx.html
- Updated: 10_ASSETS/US-MSFT/INDEX.md, synthesis.md
- Updated: 50_RESEARCH/concepts/economic-moat.md (Azure 사례 추가)
- Cross-refs: 10_ASSETS/US-GOOG/synthesis.md (cloud 비교 단락)

## [2026-05-04 10:15] query | "최근 30일 PBR<1 종목"
- Pages read: INDEX.md, 10_ASSETS/_index.md
- Result: 3 matches (KR-005380, JP-5401, US-MOS)
- Filed back: 50_RESEARCH/methodology/pbr-screening-snapshot-260504.md

## [2026-05-03 18:00] lint
- Orphan pages: 1 (KR-088980 INDEX has no inbound links) → fixed
- Stale claims: 0
- Missing concept pages: cyclical-investing → created stub
```

**컨벤션**: `## [YYYY-MM-DD HH:MM] <op> | <subject>` 일관 prefix → `Grep "^## \[" LOG.md` 한 줄로 최근 활동 조회 가능.

### 4.3 MAP.md (사람용 진입점)

변경 빈도 낮음. 신입(미래의 자신)이 "이 볼트 어떻게 쓰는 곳?"에 5분 답을 얻는 곳.

---

## 5. Frontmatter 표준 (LLM 필터링 + Dataview 양립)

```yaml
---
type: asset-index | asset-synthesis | concept | framework | plan | research | chat-extract | handoff | log | index
asset: US-MSFT                 # 해당 종목 (없으면 생략)
country: US | KR | JP | global
date: 2026-05-04               # 작성/최종갱신
status: draft | active | done | archived | stable
tags: [valuation, cyclical, dividend]
source: claude-chat | gemini-chat | self | sec-filing | s-anlyz-pipeline
related: ["[[US-MSFT/INDEX]]", "[[concepts/economic-moat]]"]
ingested_from: S-anlyz/raw/MSFT/sources/sec_10k/FY2025.html   # ingest 페이지만
last_lint: 2026-05-03          # lint 통과일 (해당 페이지만)
---
```

**`type` 어휘는 고정**. 새 type이 필요하면 PR 비슷하게 — `_templates/`에 새 템플릿 추가 + `CLAUDE.md` 의 type 목록 갱신을 한 커밋에 묶음.

---

## 6. 3대 오퍼레이션 — Ingest / Query / Lint

LLM-Wiki 이론의 핵심. **이 세 가지가 정의되지 않으면 wiki는 작동하지 않는다.**

### 6.1 Ingest (소스 통합)

**Trigger**: 사용자가 "이 자료 흡수해줘" 또는 분석 파이프가 새 산출물 생성.

**Workflow** (Claude Code가 따름):
1. 소스 식별: 종목? 개념? 거시? 채팅?
2. **소스 한 번 읽기** → 핵심 추출
3. 사용자와 takeaway 1-2문장 합의
4. 갱신 대상 페이지 결정:
   - 종목이면: `10_ASSETS/<티커>/INDEX.md` + `synthesis.md`
   - 개념 언급 시: `50_RESEARCH/concepts/<concept>.md` 갱신/생성
   - 모순 발견 시: 기존 페이지에 `> [!warning] Contradiction: ...` 콜아웃 추가
5. **`INDEX.md` 갱신** (새 페이지 추가 시)
6. **`LOG.md` append**: `## [YYYY-MM-DD HH:MM] ingest | <subject>` + 갱신 페이지 리스트
7. 사용자에게 변경 페이지 목록 제시 → 사용자 확인 → 커밋

**예시: MSFT FY2025 10-K ingest**:
```
입력: S-anlyz/raw/MSFT/sources/sec_10k/FY2025_xxx.html (raw, 불변)
영향:
  - 10_ASSETS/US-MSFT/synthesis.md  (Azure 성장률 갱신)
  - 10_ASSETS/US-MSFT/INDEX.md      (Last Analyzed 날짜)
  - 50_RESEARCH/concepts/economic-moat.md (네트워크 효과 사례 추가)
  - 50_RESEARCH/industry/cloud-infra.md   (시장점유율 갱신)
  - INDEX.md, LOG.md
```

### 6.2 Query (질문)

**Workflow**:
1. **항상 `INDEX.md` 부터 읽음** (전체 종목 폴더 grep 금지)
2. 후보 페이지 2-5개 식별 → 그것만 읽음
3. 답변 작성 + 출처 wiki링크 표시
4. **답변이 가치 있으면 wiki에 file-back**:
   - 비교/분석/연결 발견 → `50_RESEARCH/methodology/<주제>-<날짜>.md` 로 저장
   - LOG.md 에 query 기록

**금지**: 채팅 히스토리에만 남기고 끝내지 않는다. 가치 있는 발견은 반드시 wiki로 회수.

### 6.3 Lint (월 1회 건강검진)

**Trigger**: 사용자가 "lint" 또는 매월 1일 자동 (선택).

**체크 항목**:
| 검사 | 도구 |
|---|---|
| 모순: 같은 사실에 대해 다른 페이지가 다른 주장 | LLM이 종목 synthesis 교차 read |
| Stale: 6개월 이상 갱신 없는 active 페이지 | frontmatter `date` + `status` |
| Orphan: inbound 링크 0개 페이지 | Obsidian graph view + grep `[[<page>]]` |
| 누락 개념: 본문에 자주 등장하나 concept 페이지 없음 | 빈도 분석 + concepts/ 디렉토리 차이 |
| 깨진 링크: `[[xxx]]` → 실제 파일 없음 | Obsidian 자체 기능 |
| Dead artifact: `_artifacts/`에 있으나 어떤 wiki 페이지도 참조 안 함 | grep |

**산출물**: `LOG.md` 에 `## [YYYY-MM-DD] lint` 항목 + `90_ARCHIVE/lint-reports/<날짜>.md` 상세 보고서.

---

## 7. 외부 채팅 Ingest 파이프라인

### 7.1 Claude.ai

1. 월 1회 Settings → Export data → JSON 다운로드
2. `00_INBOX/chats/claude/YYYY-MM/raw.json` 저장 (gitignored)
3. Claude Code에 요청: *"이 raw.json을 종목/주제별 .md로 분리해줘. 각 .md 는 frontmatter `type: chat-extract, source: claude-chat` 부여"*
4. LLM이 `00_INBOX/chats/_processed/` 에 분리
5. 사용자가 가치 있는 5-10개 선별 → Ingest 워크플로 (§6.1) 적용 → `10_ASSETS/<티커>/_notes/` 또는 `50_RESEARCH/` 정착
6. raw.json 은 gitignore. 가공된 .md만 커밋

### 7.2 Gemini

Google Takeout → 동일 파이프라인.

### 7.3 자동화 (선택, Phase 5 이후)

- PowerShell 폴더 감시 → `00_INBOX/chats/.../raw.json` 들어오면 자동으로 Claude Code skill 호출
- Phase 5 안착 후 검토. v2.0.0 본문 범위 외.

---

## 8. 리스크 격리 마이그레이션 (Phase 0~5)

> 비개발자 멘탈 모델: **"위험한 작업 = ① 커밋 ② 새 브랜치 ③ 푸시 + 태그"**. Claude Code 가 명령어 만들고, 사용자는 승인만.

### Phase 0 — 안전망 (30분, 코드 변경 0)

- 현재 master `git status` M 다수 정리
  - 남길 변경 → 그대로 커밋 (`feat/pre-kb-v2-cleanup`)
  - 버릴 변경 → 사용자 명시 확인 (자동 폐기 절대 금지)
- 태그: `git tag v-pre-kb-v2`
- 푸시: `git push origin master --tags`
- 새 브랜치: `git checkout -b kb-v2/phase1-skeleton`

### Phase 1 — 골격 + 스키마 (2시간, 위험 0)

- **브랜치**: `kb-v2/phase1-skeleton`
- 작업:
  - `00_~90_` 빈 폴더 + `_attachments/` + `_templates/`
  - `_templates/` 5종 템플릿 (asset-INDEX, asset-synthesis, concept, plan, chat-extract)
  - **루트 `CLAUDE.md` 작성** — 볼트 스키마 본문 (이 v2 플랜의 §1~7 압축본 + 명령형 규칙)
  - 빈 `INDEX.md`, `LOG.md`, `MAP.md`
  - `.gitignore` 보강: `00_INBOX/chats/**/raw.json`, `00_INBOX/chats/**/raw/`
- 검증: Obsidian 으로 볼트 열기 → 5개 폴더 진입, 템플릿 작동 확인
- 머지: master fast-forward → 태그 `v-kb-v2-phase1`

### Phase 2 — Layer 1 자산 이관 (4시간, 위험 중)

- **브랜치**: `kb-v2/phase2-migration`
- 작업:
  - `S-anlyz*/!Report/*.{jsx,html}` → `10_ASSETS/<국가>-<티커>/_artifacts/dashboard_<날짜>.{jsx,html}`
  - `S-anlyz*/raw/screening/*` 정리 → `20_SCREENING/_artifacts/`
  - `S-anlyz*/archive/*.md` → frontmatter 부여 후 `40_PLANS/done/` 또는 `50_RESEARCH/`
  - root `HANDOFF-*.md` → `90_ARCHIVE/handoffs/`
- 세이프티:
  - **`git mv` 사용** (cp+rm 금지, 히스토리 보존)
  - **종목 1개당 1커밋** ("MSFT artifacts migration", "088980 artifacts migration")
  - 원본 폴더(`S-anlyz/!Report/`)는 **삭제하지 말고 유지** — 1주 병행 운영 후 검증되면 그때 제거 (별도 Phase 2-cleanup)
- 검증: 티커별 `_artifacts/` 폴더 더블클릭 → JSX/HTML 열림. `git log --oneline` 종목 단위 식별 가능
- 머지: → 태그 `v-kb-v2-phase2`

### Phase 3 — Layer 2 부트스트랩 (LLM이 wiki 페이지 초기 작성) (4시간, **신규**, 위험 낮음)

> v1에 없던 단계. LLM-Wiki 이론의 핵심 — **빈 폴더 ≠ wiki**. 초기 페이지가 있어야 compounding 시작.

- **브랜치**: `kb-v2/phase3-wiki-bootstrap`
- 작업 (전부 LLM 자동 + 사용자 검토):
  - 종목별 `INDEX.md` 자동 생성 (`_artifacts/` 메타 + `S-anlyz*/raw/<티커>/SOURCE_PACKAGE.json` 참조)
  - 종목별 `synthesis.md` 초안 — 가장 최근 dashboard 산출물에서 핵심 5-10 줄 추출
  - 루트 `INDEX.md` 채우기 — 모든 종목 + 기존 framework + 기존 plan 카탈로그
  - `LOG.md` 부트스트랩 항목 추가
  - `50_RESEARCH/concepts/` 에 자주 등장 개념 5개 stub 페이지 생성 (PBR / Cyclical / Moat / FCF / EPS quality)
- 사용자 검토: 종목당 30초씩 훑어보고 "오류 / 사실관계" 만 표시. 글 다듬기는 LLM
- 머지: → 태그 `v-kb-v2-phase3`

### Phase 4 — 외부 채팅 1차 흡입 (2시간, 위험 낮음)

- **브랜치**: `kb-v2/phase4-chats`
- §7 파이프라인 1회 실행: Claude.ai + Gemini 1개월 분 export
- 가공 .md 5-10개 → 종목/연구 폴더로 정착 (Ingest 워크플로 적용)
- 머지: → 태그 `v-kb-v2-phase4`

### Phase 5 — 운영 안착 (3시간, 위험 0)

- **브랜치**: `kb-v2/phase5-ops`
- Obsidian Dataview 플러그인 설치 → `INDEX.md` 동적화 (수동 표 → frontmatter 기반 자동 표)
- `MAP.md` 보강 (사람용 5분 가이드)
- **첫 lint 실행** (§6.3) → orphan / stale / missing concept 보고서
- 루트 `CLAUDE.md` 최종 확정 (Phase 1 작성 + Phase 2~4 운영 경험 반영)
- 머지: → 태그 `v-kb-v2-stable`

---

## 9. Phase E (별도, 본 v2 범위 외) — 3국 `.claude` 통합

> **사용자 결정**: 본 v2.0.0 에서는 다루지 않는다. 폴더는 `S-anlyz/`, `S-anlyz-kr/`, `S-anlyz-jp/` 그대로 유지.

이 §는 v2 운영이 안정된 뒤 별도 플랜에서 다루기 위한 **인터페이스 정의**만 둔다.

### 9.1 인터페이스 (v2가 보장하는 것)

- 볼트 루트 `CLAUDE.md` 는 `S-anlyz*/CLAUDE.md` 와 **이름·역할 분리**된 도메인. v2 어떤 단계에서도 분석 파이프 CLAUDE.md를 수정하지 않는다
- `60_AGENTS/` 폴더 **금지**. 추후 통합 작업은 별도 폴더(예: 미래의 `60_PIPELINE/`) 또는 별도 저장소에서 진행
- v2 운영 중 발견되는 3국 차이는 `LOG.md` 에 `## [YYYY-MM-DD] observation | agent-diff: ...` 형식으로 누적

### 9.2 Phase E 진입 트리거 (참고용, 본 플랜 외)

- v2 Phase 5 안착 후 최소 **2주 운영 관찰**
- A/B 비교 검증 (시범 국가 1개 → 1주 분석 결과 동등성 확인)
- 자세한 절차는 `PLAN_통합지식관리-리스크격리_260504.md` §Phase E 참조

---

## 10. 사고 시 복구 (비개발자 직접 가능)

| 사고 | 복구 명령 (Claude Code 가 만들어주고 사용자는 승인만) |
|---|---|
| "이번 phase 처음부터" | `git reset --hard <태그>` (예: `v-kb-v2-phase1`) |
| "방금 파일 이동만 무효화" | `git revert <commit-hash>` |
| "브랜치 통째로 폐기" | `git checkout master && git branch -D kb-v2/<branch>` |
| "PC 망가짐" | 다른 PC `git clone <원격URL>` → 마지막 푸시까지 복구 |
| "wiki 페이지 LLM이 잘못 갱신" | 해당 파일만 `git checkout HEAD~1 -- <path>` 후 재작성 의뢰 |
| "Phase E(미래) 통합 후 분석 회귀" | `git checkout master` 1줄 — Phase E 브랜치 무효화 |

---

## 11. 검증 체크리스트 (Phase별 통과 기준)

| Phase | 통과 기준 |
|---|---|
| 0 | `git tag` 에 `v-pre-kb-v2`, 원격 `master`/`tags` 동기화 |
| 1 | Obsidian 볼트로 열림 / 폴더 5개+ 진입 가능 / 루트 `CLAUDE.md` 존재 / 템플릿 5종 작동 |
| 2 | 모든 종목 `_artifacts/` 더블클릭 정상, `git log --oneline` 종목 단위 커밋 식별, 원본 `S-anlyz*/!Report/` 보존 |
| 3 | 모든 종목 `INDEX.md` + `synthesis.md` 존재, 루트 `INDEX.md` 카탈로그 완성, `LOG.md` 부트스트랩 항목 |
| 4 | `00_INBOX/chats/.../raw.json` 존재(미커밋), 가공된 `.md` 5+ 정착, `LOG.md` ingest 항목 |
| 5 | Dataview 동적 표 1개 작동, 첫 lint 보고서 1건, `MAP.md` 5분 가이드, 루트 `CLAUDE.md` 운영 규칙 확정 |

---

## 12. 즉시 실행 가능한 첫 액션

1. **A안 (보수적)**: Phase 0 + Phase 1만 — 안전망 + 골격. 기존 자산 무수정. 약 2.5h
2. **B안 (중간, 권장)**: Phase 0~3 — 안전망 + 골격 + 자산 이관 + **wiki 부트스트랩**. wiki가 "빈 그릇 → 살아있는 시스템"이 되는 지점까지. 약 10h, Claude Code 8할 수행
3. **C안 (적극)**: Phase 0~5 일괄 — 채팅 흡입 + 운영 안착까지. 약 15h. 시범 종목 1개로 검증 후 권장

비개발자 + Auto mode 환경에서는 **B안 (Phase 3까지)** 권장. wiki 부트스트랩까지 가야 LLM-Wiki 패턴의 가치가 체감됨. 채팅 흡입(Phase 4)과 운영(Phase 5)은 한 주 띄워도 무방.

---

## 13. 향후 확장 (v2 안착 후 검토)

### 13.1 검색 인프라 (qmd CLI)

볼트 페이지 100개 초과 시: [qmd](https://github.com/tobi/qmd) 도입 검토 — BM25+벡터 하이브리드 + LLM 재랭킹, on-device. CLI/MCP 양쪽 지원.

### 13.2 Marp 슬라이드 출력

Obsidian Marp 플러그인. wiki 페이지 → 발표 자료 즉시 변환. 종목 분석 요약, 분기 리뷰에 활용.

### 13.3 Supabase (3차 색인)

종목 50개 초과 + 정형 쿼리 니즈 ("ROE>15 ∩ PER<15 전체 종목") 발생 시. Obsidian frontmatter → Supabase row 자동 upsert (Claude Code skill). v1 §9 와 동일.

### 13.4 Phase E (`.claude` 통합)

§9 참조. v2 안착 후 별도 플랜에서.

---

## 부록 A — 루트 `CLAUDE.md` 골격 (Phase 1 작성 대상)

볼트 루트에 둘 스키마 문서. 본 플랜 §1~7 의 운영 규칙 압축본 + Claude Code 가 따를 명령형 룰.

```markdown
# Vault CLAUDE.md (LLM-Wiki Schema)

This vault is an LLM-maintained knowledge base. You are the maintainer.

## Rules
1. NEVER modify Layer 1 (raw): S-anlyz*/raw/, S-anlyz*/!Report/, _artifacts/, _attachments/, 00_INBOX/chats/.../raw.json
2. NEVER modify S-anlyz*/CLAUDE.md or S-anlyz*/.claude/ — separate domain
3. ALWAYS read INDEX.md first when receiving asset/topic queries
4. ALWAYS append to LOG.md after ingest/query/lint
5. ALWAYS ensure frontmatter on every .md you write/update
6. NEVER skip cross-reference updates: an ingest must touch INDEX.md + LOG.md + at least 1 entity/concept page

## Workflows
- Ingest: see PLAN v2.0.0 §6.1
- Query: see PLAN v2.0.0 §6.2
- Lint: see PLAN v2.0.0 §6.3
```

---

## 부록 B — Obsidian 추천 플러그인 (모두 무료)

| 플러그인 | 용도 | v2 필수도 |
|---|---|---|
| Dataview | frontmatter 기반 동적 표 | ★★★ (Phase 5) |
| Templater | 노트 생성 시 frontmatter 자동 채움 | ★★★ (Phase 1) |
| Tag Wrangler | 태그 통합 관리 | ★★ |
| Excalidraw | 손그림/다이어그램 | ★ |
| Git | 볼트 백업 (CLI git 사용 중이면 선택) | ★★ |
| Marp | 슬라이드 출력 | ★ (확장) |

---

## 부록 C — 네이밍 규칙 표준 (v1과 동일, 일부 보강)

- 종목 폴더: `<국가>-<티커>` (예: `US-MSFT`, `KR-005380`, `JP-5401`)
- 종목 산출물: `_artifacts/dashboard_<YYMMDD>.{jsx,html}`
- 플랜: `PLAN_<주제>_<YYMMDD>.md`, 버전이 있을 시 `PLAN_<주제>_v<MAJOR.MINOR.PATCH>_<YYMMDD>.md`
- 결과: `RESULT_<주제>_<YYMMDD>.md`
- Lint 보고서: `lint-report-<YYMMDD>.md` (`90_ARCHIVE/lint-reports/`)
- 분석 노트: `<YYYY-MM-DD>_<주제>.md` (`_notes/`)
- 채팅 발췌: `<source>_<YYYY-MM>_<주제>.md` (`00_INBOX/chats/_processed/` 또는 종목 `_notes/`)
- Git 태그: `v-kb-v2-<phase>`, `v-kb-v2-stable`
- Git 브랜치: `kb-v2/<phase-name>`

---

## 부록 D — v1.0과의 호환성

본 v2.0.0 은 v1.0 을 **전면 대체**한다. v1.0 `PLAN_통합지식관리체계_260504.md` 와 보완본 `PLAN_통합지식관리-리스크격리_260504.md` 는 archive에 그대로 보존하되, 신규 작업은 v2 기준으로 진행한다.

v1 → v2 마이그레이션 경로: v1 어떤 Phase도 시작하지 않은 상태이므로, v2 Phase 0 부터 그대로 시작 가능. 이미 v1 Phase 1 작업이 진행됐다면 v2 Phase 1 의 추가 항목(`INDEX.md`, `LOG.md`, 루트 `CLAUDE.md`, `_artifacts/` 분리)만 보강 후 Phase 2 로 진행.
