---
type: log
scope: projects
maintained_by: claude-code
---

# Projects Log
<!-- 포맷 규칙:
  - plan-version: [YYYY-MM-DD] — 날짜만 (버전 번호가 선후 내포, HH:MM 불필요)
  - 실시간 이벤트(phase-start/complete, ingest, query 등): [YYYY-MM-DD HH:MM]
-->
<!-- Events: decision, plan-version, result, phase-start, phase-complete, status-change, concept-extracted, theme-extracted, handoff, ingest, query, lint -->

## [2026-05-13 00:00] ingest | 5개 신규 프로젝트 wiki 부트스트랩
- 대상: anlyz-hrIndexData, interview-stt, mailing-agent, meeting-db, okr-matrix
- 각 프로젝트 {slug}.md + synthesis.md 생성
- raw coords: `10_RAW/projects/*/` (각 프로젝트 핵심 plan/result/handoff 파일 참조)

## [2026-05-12 18:28] ingest | bulk raw migration via /projects (71 files, 0 wikilinks cascaded)
- 소스: !Claude (34), HR-indexData (19, handoff 2 포함), Smartmeeting - 문서 (18)
- 슬러그별: mailing-agent=8, anlyz-hrIndexData=19, meeting-db=3, interview-stt=2, okr-matrix=30, knowledge-management=9
- cascade 갱신 wiki: 0 (WIKI에 source basename 참조 없음, basename 변경 없음)
- skip: 사전 필터 패턴 (`claude-code-best-practice-main/**`, `commands-main/**` — 외부 reference repo 다수)
- 중복 rename: handoff__HR-indexData.md, HANDOFF-1__HR-indexData.md (소스 식별자 부여)
- HR_Dashboard_Plan.md: S2 root에서 anlyz-hrIndexData/plans 로 이관

## [2026-05-05 11:59] phase-start | knowledge-management phase3-pilot
- phase: phase3-pilot
- raw coords: none (git 작업 기반)
- note: wiki bootstrap 시작.

## [2026-05-05] plan-version | knowledge-management v2.2.1
- version: v2.2.1, date: 2026-05-05
- raw coords: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.2.1_260505.md` §0 (L9~25)
- key: Pilot-first 전략, Phase 2/3 분할, 부록 A 외부 분리

## [2026-05-05] plan-version | knowledge-management v2.2.0
- version: v2.2.0, date: 2026-05-05
- raw coords: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.2.0_260505.md` §0 (L12~25)
- key: Dual-axis (Asset+Project), 3-tier navigation, Concept/Theme reverse index

## [2026-05-05] plan-version | knowledge-management v2.1.0
- version: v2.1.0, date: 2026-05-05
- raw coords: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.1.0_260505.md` §0 (L18~30)
- key: 폴더=Layer 매핑, Raw Reading Discipline 신설, Mirror Principle 명문화

## [2026-05-04] plan-version | knowledge-management v2.0.0
- version: v2.0.0, date: 2026-05-04
- raw coords: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.0.0_260504.md` §0 (L18~30)
- key: LLM-Wiki 3계층 모델 도입, Ingest/Query/Lint 3대 오퍼레이션

## [2026-05-04] plan-version | knowledge-management v1.0
- version: v1.0, date: 2026-05-04
- raw coords: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_260504.md` §header (L1~15)
- key: 최초 설계, Obsidian+frontmatter, 지식관리 체계 설계
