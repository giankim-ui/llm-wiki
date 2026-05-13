---
description: LLM-Wiki v2.2 ingest — raw 파일을 vault에 흡수해 wiki 페이지를 생성·갱신합니다.
---

사용자가 통보한 raw 파일(또는 $ARGUMENTS)을 LLM-Wiki v2.2 §6.1 워크플로우에 따라 흡수한다.

## 0. 사전 확인

1. `$ARGUMENTS` 가 비어 있으면 → AskUserQuestion 으로 **ingest 대상** (파일 경로 또는 슬러그)과 **Δ(무엇이 새로운지)** 를 질문한다.
2. 대상이 있으면 아래 단계를 순서대로 실행한다.

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
4. `20_WIKI/assets/LOG.md` — `ingest` 이벤트 append (좌표 포함)
5. 관련 `20_WIKI/concepts/`, `themes/`, `comparisons/` 데이터 포인트 갱신 (해당 시)
6. 루트 `INDEX.md` · `LOG.md` — 주요 하이라이트 판단 후 갱신

## 5. Project Ingest 순서

Agent(haiku)를 활용해 아래 갱신을 **병렬** 처리:

1. `20_WIKI/projects/<slug>/synthesis.md` — plan-version/result Δ append
2. `20_WIKI/projects/<slug>/INDEX.md` — `current_version`, `last_activity` 갱신
3. `20_WIKI/projects/INDEX.md` — Active 표 갱신
4. `20_WIKI/projects/LOG.md` — 이벤트 append (`plan-version` / `result` / `ingest`)
5. 신규 concept 도출 시 → `20_WIKI/concepts/<new>.md` 생성 + `concepts/INDEX.md` reverse index 갱신
6. 루트 `INDEX.md` · `LOG.md` 갱신

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
- **synthesis.md**: 항목당 5~10줄 상한. 원문 복제 금지. Δ(이전 항목 대비 변화)만 기록.
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
