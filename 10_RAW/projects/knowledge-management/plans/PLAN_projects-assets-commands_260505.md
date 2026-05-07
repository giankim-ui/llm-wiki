# /projects · /assets 명령 신설 + 메모리 저장

## Context

**목적**: 사용자가 좌표·Δ 등을 매번 통보하는 부담을 줄이고, LLM이 정형 이관 작업을 자동으로 수행하게 한다. AI 협업 취지에 맞춰 사용자는 의도만 통보하고 LLM이 단순 작업을 대행하는 패턴 강화.

**현황**:
- 사용자 `nayut`의 `!claudeProject` Vault는 LLM-Wiki Schema v2.2 (`PLAN_통합지식관리체계_v2.2.1_260505.md`) 기반.
- 현재 raw 자료는 분산되어 있음:
  - 프로젝트 .md: `archive/`, `S-anlyz/archive/`, `S-anlyz-kr/archive/`, `S-anlyz-jp/archive/` (총 63개)
  - 자산 분석 산출물: 3국 `!Report/` (.html/.jsx, 16개 + 스크리닝 3개), `raw/<TICKER>/SOURCE_PACKAGE.json` (5개)
- PLAN Phase 2-pilot/full 에서 수동 이관 예정이었으나, 본 명령으로 자동화하여 사용자 부담 제거.
- 기존 `/P.S`, `/R.S` 와 동일한 패턴 (사용자-글로벌 `~/.claude/commands/{name}.md`)으로 신설.

## 작업 항목

### 1. 메모리 저장 (feedback type)

**파일**: `C:\Users\nayut\.claude\projects\C--Users-nayut--claudeProject\memory\feedback_proactive_routine_work.md`

```markdown
---
name: 정형 이관·분류 작업은 LLM이 자동 수행
description: 좌표/Δ/슬러그 분류 등 규칙 기반 작업은 사용자에게 묻지 말고 LLM이 직접 처리. 모호할 때만 AskUserQuestion 사용.
type: feedback
---

좌표 통보, Δ 작성, 슬러그 분류, 파일 이관 위치 결정 등 **규칙·관례로 결정 가능한 정형 작업**은 사용자에게 묻지 않고 LLM이 자동 수행한다. 사용자는 의도("이번 분석 흡수해줘", "/assets")만 통보, 나머지(파일명 패턴 매칭, mtime → YYMMDD, 슬러그 dictionary 룩업, INDEX/LOG 갱신)는 LLM이 책임진다.

**Why**: AI 협업의 본질은 단순 업무를 대행해 사용자 인지 부하를 줄이는 것. 매번 좌표·Δ를 자연어로 통보하라는 흐름은 NotebookLM/RAG 대비 우위를 잃게 함. PLAN v2.2.1 §1.4 역할분리표가 의도한 LLM 책임 영역을 좁게 해석하지 말라는 명시 피드백 (260505).

**How to apply**:
- /projects, /assets, ingest, query 등 모든 정형 작업에서 기본 동작은 LLM 자동 수행
- 모호한 경우(파일명만으로 슬러그 결정 불가, 티커 충돌 등)에만 AskUserQuestion 사용
- 사용자에게 "어떤 좌표 봤어?" "Δ 뭐야?" 식 질문 금지. 파일 mtime, frontmatter, 본문 첫줄 등으로 LLM이 추론 후 변경 목록만 보고
```

**MEMORY.md 인덱스 추가** (`C:\Users\nayut\.claude\projects\C--Users-nayut--claudeProject\memory\MEMORY.md`):
```
- [정형 작업 자동 수행](feedback_proactive_routine_work.md) — 좌표/Δ/슬러그는 LLM 자동, 모호할 때만 AskUserQuestion
```

---

### 2. `/projects` 명령 신설

**파일**: `C:\Users\nayut\.claude\commands\projects.md`

**동작 요약**:
- 4개 archive 폴더의 .md 파일을 `10_RAW/projects/<slug>/{plans,results,handoffs,clippings}/` 로 `git mv`
- 슬러그 자동 분류 (PLAN v2.2.1 부록 F 기준)
- 모호 파일은 런타임 AskUserQuestion으로 사용자에게 슬러그 묻기

**프론트매터**:
```yaml
---
description: cwd/archive 및 3국 ~/archive 의 .md 파일을 10_RAW/projects/{슬러그}/{타입}/ 으로 일괄 이관 (git mv)
---
```

**본문 핵심 로직**:
1. **소스 폴더 (4곳)**:
   - `<cwd>/archive/`
   - `<cwd>/S-anlyz/archive/` (재귀)
   - `<cwd>/S-anlyz-kr/archive/`
   - `<cwd>/S-anlyz-jp/archive/`
2. **파일 분류 규칙 (자동)**:
   | 패턴 | 슬러그 | 타입 폴더 |
   |---|---|---|
   | `PLAN_통합지식관리*`, `PLAN_km-*`, `PLAN_raw-data-preservation*`, `PLAN_phase-model*`, `REF_CLAUDE-md_skeleton*`, `lim-wiki*` | `knowledge-management` | `plans/` |
   | `PLAN_cross-country-pipeline-sync*`, `PLAN_pipeline-sync-agent*`, `PLAN_investing-scraper*`, `PLAN_sec-scraper*`, `PLAN_us-sync-screening-cyclical*`, `PLAN_data-collector*`, `PLAN_S-anlyz-jp*`, `plan*.md`, `plan-*.md`, `plan-jp-*`, `plan-sonnet*`, `plan-industry*` | `multi-agent-stock-analysis` | `plans/` |
   | `PLAN_jp-sync-screening*`, `PLAN_edinet-api-integration*` | `screening-mode` | `plans/` |
   | `RESULT_*`, `result-*`, `result.md`, `result-2026*` | (slug는 PLAN과 동일 매핑) | `results/` |
   | `HANDOFF*` | (slug 추론: 3국 archive 면 multi-agent-stock-analysis, cwd archive HANDOFF/HANDOFF-1 은 knowledge-management) | `handoffs/` |
   | `research*.md` (research.v2/v3/v4/v5/research-v.new/research-viz/research-asset-mirae) | (PLAN과 동일 매핑: cwd archive면 km, S-anlyz면 multi-agent-stock-analysis) | `clippings/` |
   | `CLAUDE_KR*`, `jp-stock-analysis-framework*`, `jSX-HTML-변환규칙*`, `investing-scriper*`, `supervisor-v1*` | `multi-agent-stock-analysis` | `clippings/` |
3. **모호 파일 (런타임 AskUserQuestion)**:
   - `security-guide-260503.md`, `excel-py-260419.md`, `task.md` (S-anlyz-jp/), `lim-wiki-ko.md` 등
   - 옵션: knowledge-management / multi-agent-stock-analysis / screening-mode / skip
4. **중복 처리**:
   - 동일 파일명이 여러 폴더에 존재 (예: `jp-stock-analysis-framework.md` 가 S-anlyz/ 와 S-anlyz-jp/ 양쪽) → 첫 번째 mv 후 두 번째는 `<basename>_<src-folder-name>.md` 로 rename mv (예: `jp-stock-analysis-framework_S-anlyz-jp.md`)
5. **이관 방식**: `git mv <src> <dst>` (전부)
6. **빈 파일 처리**: 0 byte 파일도 이관 (`lim-wiki-ko.md` 0 byte)
7. **하위 폴더 처리**: `S-anlyz/archive/debug-archive/excel-py-260419.md` 같은 nested → flatten (`<dst>/excel-py-260419.md`)
8. **타겟 디렉토리 자동 생성**: `mkdir -p 10_RAW/projects/<slug>/{plans,results,handoffs,clippings}`
9. **종료 시 보고**:
   - 이관 파일 N개, 슬러그별 카운트
   - AskUserQuestion으로 처리한 모호 파일 목록
   - skip된 파일 목록 (있다면)
10. **LOG 갱신** (Schema v2.2 binding): `20_WIKI/projects/projects-LOG.md` 에 `## [YYYY-MM-DD HH:MM] ingest | bulk raw migration via /projects` append

---

### 3. `/assets` 명령 신설

**파일**: `C:\Users\nayut\.claude\commands\assets.md`

**동작 요약**:
- 3국 `!Report/` 의 `.html/.jsx` 를 `10_RAW/assets/<COUNTRY-TICKER>/reports/dashboard_<YYMMDD>.{html,jsx}` 로 `git mv`
- 스크리닝 파일은 `10_RAW/screening/<YYYYMMDD>/<COUNTRY>_screening.html` 로 라우팅
- 3국 `raw/<TICKER>/SOURCE_PACKAGE.json` 을 `10_RAW/assets/<COUNTRY-TICKER>/reports/SOURCE_PACKAGE_<YYMMDD>.json` 로 **`cp`** (캐시 보존)
- `Source_Packages/` 폴더는 **skip**

**프론트매터**:
```yaml
---
description: 3국 !Report 의 .html/.jsx + raw 의 SOURCE_PACKAGE.json 을 10_RAW/assets/{국가-티커}/reports/ 로 이관. 스크리닝은 10_RAW/screening/<날짜>/ 로 분리. (!Report 는 git mv, raw 는 cp 캐시 유지)
---
```

**본문 핵심 로직**:
1. **소스 → 국가 prefix 매핑**:
   - `S-anlyz/` → `US`
   - `S-anlyz-kr/` → `KR`
   - `S-anlyz-jp/` → `JP`
2. **파일 분류**:
   - `<국가-소스>/!Report/<TICKER>_분석대시보드.{html,jsx}` 또는 `<TICKER>_分析대시보드.{html,jsx}` (JP 간체) 또는 `HMC_현대자동차_분석대시보드.{html,jsx}` (KR 한글 포함)
     → 티커 추출: 첫 `_` 앞부분 (예: `088980_분석대시보드.html` → `088980`, `HMC_현대자동차_*` → `HMC`)
     → 대상: `10_RAW/assets/<COUNTRY>-<TICKER>/reports/dashboard_<YYMMDD>.{html,jsx}`
     → mtime을 YYMMDD로 변환 (예: `2026-05-03` → `260503`)
     → **`git mv`**
   - `<국가-소스>/!Report/{US|KR|JP}_스크리닝_<YYYYMMDD>.html` 또는 `{KR|JP}_スクリーニング_*.html`
     → 대상: `10_RAW/screening/<YYYYMMDD>/<COUNTRY>_screening.html`
     → 파일명에서 YYYYMMDD 추출
     → **`git mv`**
   - `<국가-소스>/raw/<TICKER>/SOURCE_PACKAGE.json`
     → 대상: `10_RAW/assets/<COUNTRY>-<TICKER>/reports/SOURCE_PACKAGE_<YYMMDD>.json` (mtime YYMMDD)
     → **`cp`** (원본 유지 — 파이프라인 캐시 재사용)
   - `<국가-소스>/raw/<TICKER>/sources/` (10-K/10-Q HTML)
     → **skip** (파이프 캐시, vault에 미러링 불필요)
   - `<국가-소스>/Source_Packages/` (S-anlyz/만 존재)
     → **skip** (레거시 구조, 사용자 명시 요청 시만)
3. **티커 ambiguity 검출**:
   - KR-088980: 사용자가 "005380" 으로도 언급 가능. 명령 실행 시 파일명 그대로 신뢰 (088980).
   - 실행 후 보고서에서 "다른 티커로 매핑 필요한 파일이 있다면 알려달라" 부기
4. **국가 한글 prefix 정리** (KR `HMC_현대자동차_*` 같은 케이스):
   - 폴더명은 `KR-HMC` 로 통일 (현대자동차 한글 부분은 무시)
5. **타겟 디렉토리 자동 생성**: `mkdir -p 10_RAW/assets/<COUNTRY-TICKER>/reports`, `mkdir -p 10_RAW/screening/<YYYYMMDD>`
6. **이미 존재하는 동일 경로**: `dashboard_260503.html` 가 이미 있으면 `dashboard_260503-v2.html` 로 충돌 회피
7. **종료 시 보고**:
   - 이관 파일 N개, 국가별 카운트, 티커별 카운트
   - skip된 파일 (sources/, Source_Packages/) 목록
   - cp된 파일 목록 (캐시 보존됨 안내)
8. **LOG 갱신**: `20_WIKI/assets/assets-LOG.md` 에 `## [YYYY-MM-DD HH:MM] ingest | bulk raw migration via /assets` append

---

## 변경 파일 목록

| 파일 | 작업 |
|---|---|
| `C:\Users\nayut\.claude\projects\C--Users-nayut--claudeProject\memory\feedback_proactive_routine_work.md` | 신규 |
| `C:\Users\nayut\.claude\projects\C--Users-nayut--claudeProject\memory\MEMORY.md` | 1줄 추가 |
| `C:\Users\nayut\.claude\commands\projects.md` | 신규 |
| `C:\Users\nayut\.claude\commands\assets.md` | 신규 |

## 핵심 참조 파일

- `C:\Users\nayut\.claude\commands\P.S.md`, `R.S.md`, `handoff.md` — 기존 명령 형식 모델
- `C:\Users\nayut\!claudeProject\CLAUDE.md` — Schema v2.2 binding (LOG 형식, status vocab, mirror principle)
- `C:\Users\nayut\!claudeProject\10_RAW\projects\knowledge-management\plans\PLAN_통합지식관리체계_v2.2.1_260505.md` 부록 F — 프로젝트 슬러그 사전, 부록 C — 네이밍 규칙
- `C:\Users\nayut\!claudeProject\S-anlyz\CLAUDE.md` — 파이프 동작 (raw/ 캐시 정책 확인 근거)

## 검증 방법

명령 신설 후 실제 실행으로 검증:

1. **`/projects` 실행**:
   - cwd = `C:\Users\nayut\!claudeProject` 에서 호출
   - 기대 결과: 63개 .md 파일이 `10_RAW/projects/{knowledge-management,multi-agent-stock-analysis,screening-mode}/{plans,results,handoffs,clippings}/` 하위로 이동
   - 모호 파일 4~7개에 대해 AskUserQuestion 발동 확인
   - `git status` 로 mv 트래킹 확인 (`R` 표시)
   - `20_WIKI/projects/projects-LOG.md` 에 ingest 항목 추가 확인
2. **`/assets` 실행**:
   - 기대 결과:
     - `S-anlyz/!Report/MOS_분석대시보드.html` → `10_RAW/assets/US-MOS/reports/dashboard_260503.html`
     - `S-anlyz-kr/!Report/HMC_현대자동차_분석대시보드.{html,jsx}` → `10_RAW/assets/KR-HMC/reports/dashboard_*.{html,jsx}`
     - `S-anlyz-jp/!Report/5401_分析대시보드.html` → `10_RAW/assets/JP-5401/reports/dashboard_260501.html`
     - `S-anlyz/!Report/US_스크리닝_20260503.html` → `10_RAW/screening/20260503/US_screening.html`
     - `S-anlyz/raw/MSFT/SOURCE_PACKAGE.json` → 원본 그대로 + 사본이 `10_RAW/assets/US-MSFT/reports/SOURCE_PACKAGE_260503.json` 에 생성
   - `20_WIKI/assets/assets-LOG.md` ingest 항목 추가 확인
3. **메모리 검증**:
   - 새 세션 시작 시 `MEMORY.md` 인덱스에 새 항목 표시 확인
4. **사후 동작 확인** (선택):
   - S-anlyz 파이프 1회 재실행 (예: `MSFT 분석`) → 캐시 hit 정상 (`raw/MSFT/SOURCE_PACKAGE.json` 보존됐기 때문)
   - 새 분석 실행 → `!Report/` 에 새 .html 생성됨 (이전 mv 영향 없음)

## 주의사항

- 본 명령 실행 후 PLAN v2.2.1 Phase 2 (raw 이관) 는 사실상 완료 상태가 됨. Phase 3 (wiki 부트스트랩) 는 별도 ingest 흐름으로 진행.
- mv 작업이라 git history 추적되지만, 사용자가 직접 `git push` 하지 않는 한 원격은 미반영.
- 명령 본문은 한국어 imperative + 절차 명세. P.S/R.S 와 동일하게 LLM이 명령 본문을 읽고 절차 수행 (skill = LLM 자체가 실행).
