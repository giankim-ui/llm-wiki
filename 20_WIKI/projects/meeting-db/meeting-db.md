---
type: project-index
project: meeting-db
date: 2026-05-13
status: active
last_activity: 2026-05-11
current_phase: operations
current_version: v1.0
done_criteria: "파이프라인 안정 운영 + meeting_dashboard.html 자동 갱신 유지"
tags:
  - meeting-db
  - hr-meeting
  - sqlite
  - pipeline
  - stt
themes: []
concepts: []
data_points: 3
last_lint: 2026-05-13
mirrors_raw: "[[result-pipeline-mt-260511]]"
---

# meeting-db — Project Index

## Overview
HR 인사혁신팀 회의록 STT 텍스트를 `/pipeline-mt` 스킬로 5섹션 요약 마크다운으로 변환한 뒤, `sync.py`로 SQLite DB(`hr_meetings.db`)에 upsert하고 `meeting_dashboard.html`을 자동 재생성하는 파이프라인. 현재 22개 회의록 DB 적재 완료 상태로 운영 중.

## Status & Progress
| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| 파이프라인 구축 | done | — | 2026-05-11 | STEP 1 요약 + STEP 2 DB sync |
| 4자리 시각 형식 파일명 버그 수정 | done | 2026-05-11 | 2026-05-11 | FILENAME_RE `\d{2}` → `\d{2,4}` |
| 5/6 회의록 2건 제거 | done | 2026-05-11 | 2026-05-11 | DB + ingestion_log + HTML 재생성 |
| 정기 운영 | active | — | — | 신규 STT 파일 발생 시 /pipeline-mt 실행 |

## Key Plans & Results
| 유형 | Date | Summary | Raw |
|---|---|---|---|
| plan (ax-batch-resume) | — | AX batch 재개 가이드 | [[plan-ax-batch-resume-guide]] |
| result: pipeline-mt | 2026-05-11 | 7개 파일 처리, 4자리 시각 형식 버그 수정, 22개 기준 재생성 | [[result-pipeline-mt-260511]] |

## Architecture
```
STT txt
  └── /pipeline-mt STEP 1 → 20_Summary/*.md (5섹션 마크다운 요약)
  └── /pipeline-mt STEP 2 → sync.py → hr_meetings.db upsert
                                     → meeting_dashboard.html @@AUTO_*@@ 갱신
```

- `meeting_id`: `f"{ymd}_{nn}"` 형태 (예: `20260430_1554`)
- sync.py: `file_ingestion_log` 기반 변경 감지, meetings + action_items(CASCADE) 구조
