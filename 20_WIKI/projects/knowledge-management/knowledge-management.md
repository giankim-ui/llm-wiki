---
type: project-index
project: knowledge-management
date: 2026-05-05
status: active
last_activity: 2026-05-05
current_phase: phase3-pilot
current_version: v2.2.1
done_criteria: "Pilot 검증 게이트 합격 후 Phase 2-full / 3-full 완료"
tags:
  - knowledge-management
  - obsidian
  - llm-wiki
  - vault
themes: []
concepts: [llm-wiki-pattern, mirror-principle, raw-reading-discipline]
data_points: 6
last_lint: 2026-05-05
mirrors_raw: "[[PLAN_통합지식관리체계_v2.2.1_260505]]"
---

# knowledge-management — Project Index

## Overview
흩어진 투자 분석 자료(JSX/HTML 대시보드, plan/result 문서, AI 채팅 기록)를 LLM-Wiki 3계층 모델로 통합하는 vault 구축 프로젝트. 사용자는 사고하고 LLM이 유지보수하는 compounding 지식 베이스 목표.

## Status & Progress
| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| Phase 0 (git 초기화) | done | 2026-05-05 | 2026-05-05 | 브랜치 전략, 태그 체계 수립 |
| Phase 1 (vault skeleton) | done | 2026-05-05 | 2026-05-05 | 폴더 구조, 템플릿, nav stub |
| Phase 2-pilot (raw 이관) | done | 2026-05-05 | 2026-05-05 | MSFT 3파일 + km plan 8파일 |
| Phase 3-pilot (wiki 부트스트랩) | active | 2026-05-05 | — | MSFT + km wiki 1+1개 |
| Pilot 검증 게이트 | — | — | — | Obsidian wikilink 동작 검증 |
| Phase 2-full / 3-full | — | — | — | 나머지 자산·프로젝트 이관 |

## Plan Versions
| Version | Date | Key Changes | Raw |
|---|---|---|---|
| v1.0 | 2026-05-04 | 최초 통합 지식 관리 체계 설계 | [[PLAN_통합지식관리체계_260504]] |
| v2.0.0 | 2026-05-04 | LLM-Wiki 3계층 모델 도입, Ingest/Query/Lint 3대 오퍼레이션 | [[PLAN_통합지식관리체계_v2.0.0_260504]] |
| v2.1.0 | 2026-05-05 | 폴더=Layer 매핑 명확화, Raw Reading Discipline 신설, Mirror Principle 명문화 | [[PLAN_통합지식관리체계_v2.1.0_260505]] |
| v2.2.0 | 2026-05-05 | Dual-axis (Asset+Project), 3-tier navigation, Concept/Theme reverse index | [[PLAN_통합지식관리체계_v2.2.0_260505]] |
| v2.2.1 | 2026-05-05 | Pilot-first 권장, Phase 2/3 분할, 부록 A 외부 분리 | [[PLAN_통합지식관리체계_v2.2.1_260505]] |

## Key Decisions
→ decisions.md 에 상세

## Concept Links
- [[llm-wiki-pattern]]
- [[mirror-principle]]
- [[raw-reading-discipline]]

## Handoffs
| Handoff | Date | From → To | Raw |
|---|---|---|---|
| HANDOFF.md | 2026-05-05 | Phase 1 완료 → Phase 2 | [[HANDOFF]] |
| HANDOFF-1.md | 2026-05-05 | Phase 2-pilot 완료 → Phase 3-pilot | [[HANDOFF-1]] |
