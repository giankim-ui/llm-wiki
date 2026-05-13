---
type: project-index
project: okr-matrix
date: 2026-05-13
status: active
last_activity: 2026-05-11
current_phase: v2.2-ops
current_version: v2.2
done_criteria: "Supabase 로그인 아키텍처 결정 + 개인용/회사용 분리 운영 안정화"
tags:
  - okr-matrix
  - typescript
  - webapp
  - okr
  - meeting-dashboard
  - supabase
themes: []
concepts: []
data_points: 5
last_lint: 2026-05-13
mirrors_raw: "[[result-okr-integration-v2.2]]"
---

# okr-matrix — Project Index

## Overview
TypeScript 기반 OKR Matrix 웹앱. Objective → KR → Task → SubTask 계층 관리, Meeting Dashboard(`meeting_dashboard.html`)와 iframe 통합, 팀원별 localStorage 분리. 현재 v2.2(Meeting-Dashboard 통합 완료) 운영 중이며, Supabase 로그인 연동을 통한 스마트폰·외부 접근 방안 검토 중.

## Status & Progress
| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| OKR-Meeting Dashboard 통합 (v2.2) | done | 2026-04-22 | 2026-04-22 | snake_case 마이그레이션, 공유 Task 창고, 배분 모달 KR 드롭다운, postMessage 파이프라인 |
| TO-DO → OKR Task 동기화 버그 수정 | done | 2026-04-22 | 2026-04-22 | saveDistribution + syncSharedTask 완전 재작성 |
| KR 복사 기능 | — | — | — | plan-okr-kr-copy v1.1 있음 |
| Supabase 로그인 아키텍처 | active | 2026-05-11 | — | 개인용(Supabase) vs 회사용(MDB) 분리 운영 결정 |

## Key Plans
| Version | Date | Key Changes | Raw |
|---|---|---|---|
| plan(okr v0.5) | 초기 | OKR Matrix 앱 초기 설계 | [[plan(okr.v0.5)]] |
| plan-okr-integration-p1-p5 | — | Meeting Dashboard 통합 P1~P5 | [[plan-okr-integration-p1-p5]] |
| plan-okr-integration-v2.1 | — | v2.1 통합 계획 | [[plan-okr-integration-v2.1]] |
| plan-okr-task-sync-fix v1.0 | 2026-04-22 | Task 동기화 버그 수정 계획 | [[plan-okr-task-sync-fix-v1.0]] |
| plan-okr-kr-copy v1.1 | — | KR 복사 기능 | [[plan-okr-kr-copy-v1.1]] |
| plan-logIn-supabase-MDB | 2026-05-11 | Supabase 로그인 아키텍처 검토 | [[plan-logIn-supabase-MDB-260511]] |

## Key Results
| Result | Date | Summary | Raw |
|---|---|---|---|
| result-okr-integration-v2.2 | 2026-04-22 | OKR-Meeting Dashboard 통합 완료 | [[result-okr-integration-v2.2]] |
| result-okr-task-sync-fix v1.0 | 2026-04-22 | Task 동기화 버그 수정 완료 | [[result-okr-task-sync-fix-v1.0]] |

## Architecture Decision (2026-05-11)
- Supabase MDB 연동 불가(iframe 로그인 파이프라인 충돌)
- **결론**: 개인용(Supabase, 스마트폰·외부 접근) vs 회사용 MDB는 별도 운영
- 가장 합리적: Supabase = 개인 OKR 관리용, MDB = 회사 업무 회의록 대시보드용
