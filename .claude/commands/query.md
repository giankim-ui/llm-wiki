---
description: LLM-Wiki v2.2 query — INDEX부터 drill-down으로 답하고, 가치 있는 발견을 20_WIKI/methodology/ 로 file-back 회수합니다.
---

사용자 질문($ARGUMENTS)을 LLM-Wiki v2.2 §6.2 워크플로우에 따라 답하고, 가치 있는 발견을 wiki로 회수한다.
이론 근거: `[[llm-wiki-pattern]]` — 채팅에만 남기지 않고 compounding artifact로 누적.

## 0. 질문 정규화

- `$ARGUMENTS` = 질문. 비어있으면 사용자에게 질문 요청 (AskUserQuestion 가능).
- 복수 질문이면 분해 후 각각 처리.
- **query scope 판정**: cross-axis(전체) / asset(종목) / project(프로젝트) / 개념.

## 1. INDEX 진입 (scope 분기 — BINDING)

전체 폴더 grep 금지 (컨텍스트 폭발 방지). scope에 따라 진입점 결정:

| scope | 진입 INDEX |
|------|-----------|
| cross-axis | root `INDEX.md` |
| asset | `20_WIKI/assets/assets-INDEX.md` |
| project | `20_WIKI/projects/projects-INDEX.md` |
| 개념/방법론 | `20_WIKI/concepts/concepts-INDEX.md`, `20_WIKI/methodology/methodology-INDEX.md` |

## 2. Drill-down

INDEX에서 후보 페이지 2~5개 식별 → **그것만** Read. 처음부터 종목/주제 폴더 전수 grep 금지.

## 2b. Raw 필요 시 (Raw Reading Discipline §6.0 — BINDING)

- raw 파일 **통째 Read 절대 금지**. 좌표(item × 버전/날짜 × 섹션/Item) 먼저 결정.
- 좌표 불명 시 `20_WIKI/concepts/sources/...-structure.md` 참조 → 그래도 모르면 사용자에게 질문.
- **`10_RAW/` 는 읽기 전용 — /query 는 raw 를 절대 수정·생성하지 않는다** (Rule 1).

## 3. 답변 작성

- 답변 + 출처 표시. 모든 출처는 `[[wikilink]]` (raw 참조도 `[[filename]]` — **backtick 경로 금지**, Mirror Principle 4).

## 4. file-back 판정

| 구분 | 기준 | 처리 |
|------|------|------|
| **회수 대상** | 비교 / 분석 / 여러 페이지 연결에서 나온 새 인사이트 | Step 5 노트 생성 |
| **회수 제외** | 단일 페이지 사실조회 / 기존 노트로 완결 / 발견 없음 | 노트 생성 안 함 (Step 6 query 로그 선택) |
| **중복 질문** | 동일 주제 기존 노트 존재 | **신규 생성 금지** → 기존 노트 `## Answer`/`## Finding`에 Δ append (compounding) |

## 5. 노트 생성/갱신 (haiku Agent 의무 — Agent Dispatch Policy)

`_templates/methodology-note.md` 기반으로 `20_WIKI/methodology/<주제-kebab>-<YYMMDD>.md` 생성:

- **파일명**: 주제 kebab-case ≤24자 + `-YYMMDD`. 동일 slug+날짜 충돌 시 `-b`/`-c` suffix.
- frontmatter: `type: research`, `scope: methodology`, `tags:`(빈 block — `[]` 금지), `question:` 채움.
- raw 직접 파생 노트만 `mirrors_raw: "[[filename]]"` 필수 (일반 종합물은 `## Pages Read` 로 출처 대체).

## 6. INDEX/LOG 갱신 (haiku Agent)

- `20_WIKI/methodology/methodology-INDEX.md` `## All Notes` 행 추가 (네비게이션 갱신 — 자체 LOG 행 미기록).
- root `LOG.md` 에 노트 1건당 1행:
  - `| HH:MM | query | [[note]] | 요약≤60자 |`
  - 시간 = 노트 ctime, `## YYYY-MM-DD` 헤더는 **ctime 날짜** 기준 (LOG-01). 같은 날 표에 시간 오름차순 삽입.

## 금지 (BINDING)

- 채팅 히스토리에만 남기고 끝내기 (가치 있는 발견은 반드시 wiki 회수).
- LOG/synthesis 이벤트에 `ingest` 사용 → `event-vocab-guard.py` 훅이 차단 (LOG-02). query 이벤트만 사용.
- `10_RAW/` 수정·생성 / backtick 경로 / `tags: []` inline.
