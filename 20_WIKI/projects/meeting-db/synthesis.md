---
type: project-synthesis
project: meeting-db
updated: 2026-05-13
tags:
  - meeting-db
  - pipeline
  - synthesis
---

# meeting-db — Synthesis

## [2026-05-13] ingest | 프로젝트 wiki 부트스트랩
- raw coords: `10_RAW/projects/meeting-db/results/result-pipeline-mt-260511.md`
- 프로젝트 최초 wiki 등록. 파이프라인 운영 중, 22개 회의록 DB 적재 완료.

## [2026-05-11] result | pipeline-mt + 4자리 시각 형식 버그 수정
- raw coords: `10_RAW/projects/meeting-db/results/result-pipeline-mt-260511.md`
- 7개 미처리 파일 요약 처리 완료. sync.py FILENAME_RE `\d{2}` → `\d{2,4}` 수정으로 1554·1630 등 HH:MM 시각 형식 파일명 지원. 총 22개 기준 HTML 재생성.
- Δ: ingestion_log 별도 삭제 필수 확인(hash 충돌 방지 목적).

## [2026-05-11] result | 5/6 회의록 2건 제거
- raw coords: `10_RAW/projects/meeting-db/results/result-pipeline-mt-260511.md` (purge 관련 내용)
- 원본 파일 사용자 삭제 후 요약·DB·ingestion_log 일괄 제거. ON DELETE CASCADE로 action_items 자동 삭제. sync.py 재실행으로 22개 기준 재생성.
