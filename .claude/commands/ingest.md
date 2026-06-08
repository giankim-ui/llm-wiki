---
description: LLM-Wiki v2.2 ingest — raw 파일을 vault에 흡수해 wiki 페이지를 생성·갱신합니다.
---

사용자가 통보한 raw 파일(또는 $ARGUMENTS)을 LLM-Wiki v2.2 §6.1 워크플로우에 따라 흡수한다.

## 0. 사전 확인 (자동 스캔 우선)

### 0-A. `$ARGUMENTS` 가 있으면 → 해당 파일/슬러그로 바로 진행.

### 0-B. `$ARGUMENTS` 가 없으면 → **자동 스캔** (AskUserQuestion 금지):

1. **git diff HEAD 수집** — `git diff --name-only HEAD -- 10_RAW/projects/` + `git ls-files --others --exclude-standard 10_RAW/projects/` 로 미커밋 파일 전수 수집.
2. **synthesis 비교** — 각 슬러그의 `20_WIKI/projects/<slug>/synthesis.md` 에서 `[[filename]]` wikilink를 추출. 수집된 파일 중 wikilink가 없는 것 = 미반영 대상.
3. **보고 후 확인** — 다음 형식으로 보고:
   ```
   [/ingest 자동 스캔] 미반영 파일 N개
   - anlyz-hrIndexData: A개 (파일명 목록)
   - knowledge-management: B개
   - ...
   처리할까요?
   ```
   사용자 확인(yes/진행) 후에만 Step 1~7 실행.
4. 미반영 파일이 0개면 `"[/ingest] 모든 10_RAW 파일이 synthesis에 반영되어 있습니다."` 출력 후 종료.

## 1. 축 판별 (Asset vs Project)

| 조건 | 축 |
|------|-----|
| 티커·종목명 포함, `10_RAW/assets/` 경로 | **Asset** |
| 프로젝트 slug, plan/result/handoff 파일 | **Project** |
| 채팅 기록 (.json/.md) | 종목·프로젝트 매핑 먼저 판별 |

## 2. Raw 파일 안착 확인 (INGEST ORDER — BINDING)

wiki 페이지 생성 **전**, `10_RAW/` 에 raw 파일이 반드시 먼저 존재해야 한다.

- 없으면 → 사용자에게 raw 파일 경로를 요청하거나 `10_RAW/` 이관 먼저 진행.
- `mirrors_raw` 는 `10_RAW/` 내 실제 파일만 가리켜야 한다 (외부 경로 INVALID).

## 3. Raw Reading Discipline (§6.0 — BINDING)

- raw 파일 **통째 Read 절대 금지**. 좌표(연도 × 섹션/Item)를 먼저 결정.
- 좌표 불명 시: `20_WIKI/concepts/sources/...-structure.md` 참조 → 후보 좌표 결정 → 그래도 모르면 사용자에게 질문.
- LOG.md 기록 시 raw read 좌표 또는 `none(이미 알고 있음)` 을 반드시 명시.

## 4. Asset Ingest 순서

Agent(haiku)를 활용해 아래 갱신을 **병렬** 처리 (독립 작업은 단일 메시지에서 동시 호출):

1. `20_WIKI/assets/<티커>/synthesis.md` — compounding Δ 5~10줄 append (원문 복제 금지)
2. `20_WIKI/assets/<티커>/INDEX.md` — `last_analyzed`, `data_points` 갱신
3. `20_WIKI/assets/INDEX.md` — Recently Analyzed 행 갱신
4. `20_WIKI/assets/LOG.md` 및 루트 `LOG.md` — **처리된 raw .md 파일별로 1행씩 append** (batch 요약 금지). 시간 = 파일 최초 생성 시각(ctime). 표 행은 **시간 오름차순** 정렬. synthesis.md 표 행 1줄 요약 = LOG 1줄 요약 = 동일 granularity. **이벤트 = `ingest` 절대 금지** — 허용 이벤트는 CLAUDE.md `LOG Event Vocabulary (BINDING)` 13개를 따른다.
5. 관련 `20_WIKI/concepts/`, `themes/`, `comparisons/` 데이터 포인트 갱신 (해당 시)
6. 루트 `INDEX.md` · `LOG.md` — 주요 하이라이트 판단 후 갱신

## 5. Project Ingest 순서

Agent(haiku)를 활용해 아래 갱신을 **병렬** 처리:

1. `20_WIKI/projects/<slug>/synthesis.md` — **표 형식** 행 추가 (아래 §6 양식 참조). 날짜 내림차순. 이벤트 = `ingest` 금지.
2. `20_WIKI/projects/<slug>/INDEX.md` — `current_version`, `last_activity` 갱신 + `## Recently Done` 표에 `result-*`·`handoff-*` 파일 행 prepend (날짜, [[파일]], 1줄 요약). 표가 없으면 `## Key Decisions` 앞에 생성. 90일 초과 항목은 trim (최대 10행 유지). **주의**: `## Recently Done` 아래 HTML 주석(`<!-- -->`) 사용 시 주석과 표 헤더 사이에 반드시 빈 줄 1개 삽입 — 없으면 Obsidian이 표를 raw 텍스트로 렌더링함.
3. `20_WIKI/projects/INDEX.md` — Active 표 갱신
4. `20_WIKI/projects/LOG.md` 및 루트 `LOG.md` — **처리된 raw .md 파일별로 1행씩 append** (batch 요약 금지). 시간 = 파일 최초 생성 시각(ctime). 표 행은 **시간 오름차순** 정렬. 파일명 prefix 기준: `plan-*` → `plan-version`, `result-*` → `result`, `handoff-*` → `handoff`. synthesis.md 표 행 1줄 요약 = LOG 행 1줄 요약 = 동일 granularity. **이벤트 = `ingest` 절대 금지** — 허용 이벤트는 CLAUDE.md `LOG Event Vocabulary (BINDING)` 13개를 따른다.
5. 신규 concept 도출 시 → `20_WIKI/concepts/<new>.md` 생성 + `concepts/INDEX.md` reverse index 갱신
6. 루트 `INDEX.md` · `LOG.md` 갱신

## 5.5. DAILY.md 갱신

모든 wiki 파일 업데이트 후 반드시 실행:

```
python scripts/daily_brief.py
```

`--skip-if-today` 인자 사용 **금지** — 항상 최신 상태로 재생성.

## 6. Wiki 페이지 작성 규칙

- **frontmatter 필수**: `type`, `date`, `status`, `mirrors_raw` 등 §5.1 표준 준수
- **tags**: block sequence 형식만 허용
  ```yaml
  tags:
    - foo
    - bar
  ```
  inline array `tags: [foo]` 금지 — Obsidian 유형 오류 발생
- **wikilink**: raw 파일 참조는 반드시 `[[filename]]` — 백틱 경로 금지
- **synthesis.md**: **표 형식 — 날짜 내림차순**. 날짜 헤더 `## YYYY-MM-DD` + 표 헤더 1회. 같은 날이면 기존 표에 행 추가(시간 오름차순). 열 구성:
  ```
  | 시간 | 이벤트 | 파일 | 1줄 요약 |
  |---|---|---|---|
  | HH:MM | plan-version | [[filename]] | ≤60자 요약 |
  ```
  - 시간 = 파일 ctime (불명 시 `—`)
  - 이벤트 = `ingest` **절대 금지**. 허용 이벤트는 CLAUDE.md `LOG Event Vocabulary (BINDING)` 13개.
  - 파일 = `[[basename]]` wikilink (확장자 없이)
  - 1줄 요약 = Δ 핵심 1문장 ≤60자. 원문 복제 금지.
- **status 변경**: 사용자 confirm 후에만. LLM은 제안만.

## 7. 완료 보고

변경된 파일 목록을 사용자에게 제시 후 **커밋은 사용자가 확인한 다음에만** 진행:

```
## Ingest 완료 — <대상명> (<날짜>)

### 갱신된 파일
- 20_WIKI/...
- 20_WIKI/...
- LOG.md  (raw read 좌표: <좌표 또는 none>)

### 신규 생성
- (없으면 생략)

### 권장 커밋 메시지
ingest: <대상명> <날짜>
```
