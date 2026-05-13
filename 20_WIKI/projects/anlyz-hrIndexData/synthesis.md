---
type: project-synthesis
project: anlyz-hrIndexData
updated: 2026-05-13
tags:
  - hr-analytics
  - synthesis
---

# anlyz-hrIndexData — Synthesis

## [2026-05-13] ingest | 프로젝트 wiki 부트스트랩
- raw coords: `10_RAW/projects/anlyz-hrIndexData/handoffs/handoff__HR-indexData.md` §A·§B·§E
- 프로젝트 최초 wiki 등록. HR 대시보드 재설계 분석·설계 완료, DuckDB 인원현황 파이프라인 P2 완료(8,205명 검증).
- Phase 1 핵심 미결: HCROI 파이프라인 진행 중 + D1/D2/D3 의사결정 대기.

## [2026-05-12] result | HR 인원현황 파이프라인 P2 완료
- raw coords: `10_RAW/projects/anlyz-hrIndexData/results/result-hr-pipeline-260512.md`
- 3개년(2023·2024·2025) 인원현황 DuckDB 적재 완료. 버그 5개 수정(bu_name_to_id parent_id scope 추가, emp_type_columns 명시적 6컬럼 매핑, data_start_row=7). 최종 합계 8,205명(앵커 8,197 ±15 ✓).
- `_preflight.py` + playbook.md 작성 — 다음 파이프라인(인건비·퇴사율) 재사용 가능.
