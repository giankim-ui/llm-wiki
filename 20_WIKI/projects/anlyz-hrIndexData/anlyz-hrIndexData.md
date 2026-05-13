---
type: project-index
project: anlyz-hrIndexData
date: 2026-05-13
status: active
last_activity: 2026-05-12
current_phase: phase1-pipeline
current_version: v1.0
done_criteria: "Phase 1 Quick Win 8 KPI 실데이터 산출 완료 + 2026.Q2 인사위원회 시범 양식 1차안 제출"
tags:
  - hr-analytics
  - people-analytics
  - hr-kpi
  - duckdb
  - dashboard
themes: []
concepts: []
data_points: 3
last_lint: 2026-05-13
mirrors_raw: "[[handoff__HR-indexData]]"
---

# anlyz-hrIndexData — Project Index

## Overview
풀무원 인사위원회 보고용 HR People Analytics 대시보드 재설계 프로젝트. 2023.02~2026.Q1 인사위원회 PPTX 13개 챕터를 JSON 추출 후 ISO 30414 / Saratoga / SHRM 표준 기반 6대 KPI 축 24개 KPI 체계를 설계했다. DuckDB 파이프라인으로 3개년(2023·2024·2025) 인원현황 적재 완료, HCROI 등 핵심 KPI 자동 산출 파이프라인 구축 진행 중.

## Status & Progress
| Phase                        | Status | Started    | Completed  | Notes                                       |
| ---------------------------- | ------ | ---------- | ---------- | ------------------------------------------- |
| 분석·설계                        | done   | 2026-05-08 | 2026-05-08 | PPTX 13개 챕터 추출, 8가지 보고 한계 진단, 24개 KPI 체계 설계 |
| Phase 1 (인원현황 파이프라인)         | done   | 2026-05-12 | 2026-05-12 | 3개년 DuckDB 적재 8,205명 검증 완료                  |
| Phase 1 (HCROI 파이프라인)        | active | 2026-05-12 | —          | 급여·손익 연계 HCROI 자동 산출 진행                     |
| Phase 1 (전체 8 KPI Quick Win) | —      | —          | —          | ERP+급여+손익원장 기반 즉시 산출 가능 8 KPI               |
| Phase 2 (시각화·Power BI)       | —      | —          | —          | D1·D4 의사결정 완료 후 진입                          |
| Phase 3 (예측·시나리오)            | —      | —          | —          | 2027~ HCM AX Phase 2 연동                     |

## Key Plans
| Version | Date | Key Changes | Raw |
|---|---|---|---|
| HR_Dashboard_Plan (v1) | 2026-05-08 | 초안 (787줄, 12장 ASCII 목업, 24개 사례 링크) | [[HR_Dashboard_Plan]] |
| plan-hcroiRe v2.0.0 | 2026-05-12 | HCROI 산출 재설계 | [[plan-hcroiRe-260512-v2.0.0]] |
| plan-hc-schema | 2026-05-12 | 인원현황 DuckDB 스키마 설계 | [[plan-hc-schema-260512]] |

## Key Results
| Result | Date | Summary | Raw |
|---|---|---|---|
| result-hr-pipeline | 2026-05-12 | 3개년 인원현황 DuckDB 적재 P2 완료, 8,205명 검증 | [[result-hr-pipeline-260512]] |
| result-hcroi-ofs | 2026-05-12 | HCROI 오프사이클 산출 | [[result-hcroi-ofs-260512]] |
| result-hcroi-aud-fix | 2026-05-12 | HCROI 감사 수정 | [[result-hcroi-aud-fix-260512]] |

## Open Decisions
| # | 안건 | Owner | Due |
|---|---|---|---|
| D1 | Engagement 측정 도구 (Q12 vs OHI vs eNPS) | CHO | 2026-Q2 |
| D2 | 핵심인재(High-Performer) 정의 | CHO + 경영기획 | 2026-Q2 |
| D3 | TCOW 산식 — 가맹점주/특수고용 포함 여부 | CFO + CHO | 2026-Q2 |
| D4 | 시각화 도구 (Power BI / Tableau / 자체) | DT + CHO | 2026-Q3 |

## Handoffs
| Handoff | Date | Raw |
|---|---|---|
| handoff__HR-indexData | 2026-05-08 | [[handoff__HR-indexData]] |
| HANDOFF-1__HR-indexData | 2026-05-11 | [[HANDOFF-1__HR-indexData]] |
| handoff-schema-260511 | 2026-05-11 | [[handoff-schema-260511]] |
