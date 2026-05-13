---
type: project-synthesis
project: knowledge-management
date: 2026-05-05
status: active
mirrors_raw: "[[PLAN_통합지식관리체계_v2.2.1_260505]]"
related: [llm-wiki-pattern, mirror-principle, raw-reading-discipline]
---

# knowledge-management — Synthesis

<!-- compounding log: 항목당 5~10줄, Δ vs prior. plan 본문 복제 금지. -->

## [2026-05-04] plan-version | v1.0
- **Δ vs prior**: 신규 프로젝트. 투자 자료 통합 필요성 인식에서 출발.
- **Key decision**: Obsidian + frontmatter 기반 단일 vault 선택. AI 채팅 기록 미통합은 한계로 남음.
- **Methodology insight**: 현황 진단 → 옵션 비교(A/B/C) → B 하이브리드 선택 방식 도입.
- **Concepts extracted**: 없음 (LLM-Wiki 이론 도입 이전)
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_260504.md` §1, §2

## [2026-05-04] plan-version | v2.0.0
- **Δ vs prior**: LLM-Wiki 패턴 도입으로 RAG 대비 compounding wiki 우위 논거 확립. 3계층(Raw/Wiki/Schema) 모델 채택.
- **Key decision**: `60_AGENTS/` 폴더 제거 — `.claude/` 정책 위배. 3국 통합은 Phase E로 후행.
- **Methodology insight**: INDEX.md + LOG.md + MAP.md 메타파일 분리 원칙 (카탈로그·시간선·사람용 입장 분리).
- **Concepts extracted**: llm-wiki-pattern, 3-tier navigation (초기)
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.0.0_260504.md` §0

## [2026-05-05] plan-version | v2.1.0
- **Δ vs prior**: "폴더 prefix = Layer" 원칙 도입으로 `10_RAW/` vs `20_WIKI/` 경계 명확. MOS 사건 이후 Raw Reading Discipline 신설.
- **Key decision**: synthesis.md는 5~10줄 compounding log — 분석 본문 복제 금지. wiki 가치는 cross-cutting 페이지에 있음.
- **Methodology insight**: 좌표(item × section) 없이 raw 통째 Read 금지 — token economy 강제.
- **Concepts extracted**: raw-reading-discipline, mirror-principle
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.1.0_260505.md` §0

## [2026-05-05] plan-version | v2.2.0
- **Δ vs prior**: Asset only → Asset + Project dual axis. 프로젝트 운영 pain (진행중 뭐?, 끝났나?, 유사한 거?)을 vault가 직접 해결.
- **Key decision**: 단일 vault 확정 (dual vault 검토 후 cross-axis wikilink 강점으로 단일 채택).
- **Methodology insight**: Concept/Theme reverse index 도입 — "어느 concept이 어느 project에서?" 역색인 자동 유지.
- **Concepts extracted**: dual-axis, concept-reverse-index
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.2.0_260505.md` §0

## [2026-05-05] plan-version | v2.2.1
- **Δ vs prior**: Pilot-first 전략 도입으로 13h 일괄 구현 리스크 분산. Phase 2/3 각 pilot(1h)+full(4h)로 분할.
- **Key decision**: 부록 A(CLAUDE.md 골격) 외부 분리 → `REF_CLAUDE-md_skeleton_260505.md`. plan 수정과 골격 갱신 독립 가능.
- **Methodology insight**: 검증 게이트(9항목) 도입 — pilot 합격 후에만 full 진행하는 안전장치.
- **Concepts extracted**: pilot-gate, phase-isolation
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.2.1_260505.md` §0, Phase 3-pilot

## [2026-04-27] result | organize.py .done 마커 지원 추가
- **Δ vs prior**: result*.md 없이 완료된 프로젝트를 `.done` 빈 파일 마커로 인식. OKR 외 6개 프로젝트 완료 처리.
- **Key decision**: `.done` mtime을 집계에서 제외 — 마커 생성일이 "마지막 활동일" 표시를 덮지 않도록.
- **Raw coords**: `10_RAW/projects/knowledge-management/results/result-organize-done-marker.md` §요약·핵심설계결정

## [2026-04-28] result | 검색 탭 사이드바 레이아웃 이식
- **Δ vs prior**: meeting_dashboard.html 검색 탭을 flat 구조에서 월별 폴더 사이드바 + 카드 그리드 2열 레이아웃으로 개선.
- **Key decision**: `#searchFilters`에 `display:none` 유지 — sync.py `@@AUTO_FILTER_*@@` 마커 보존.
- **Raw coords**: `10_RAW/projects/knowledge-management/results/result-search-tab-sidebar-layout.md` §요약·핵심설계결정

## [2026-05-11] result | organize.py 20-Obsidian 폴더 스캔 추가
- **Δ vs prior**: !Claude 단독 → !Claude + 20-Obsidian 통합 인덱싱. `plan*`·`result*`·`research*.md`만 추적해 OneDrive I/O 부하 최소화.
- **Key decision**: `[Ob]` 접두사로 Obsidian 항목 시각 구분, 출력(index/tags/recent)은 `!Claude`로 단일화.
- **Raw coords**: `10_RAW/projects/knowledge-management/results/result-ob-scan-add-260511.md` §요약·핵심설계결정

## [2026-05-11] plan-version | LLM-Wiki interview vault 구조 계획
- **Δ vs prior**: GitHub 스켈레톤(`giankim-ui/llm-wiki`) 활용해 interview_STT / interview_records 폴더 기반 LLM-Wiki 구조 신설 계획.
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/plan-llmWiki-interview-260511.md` (전문)

## [2026-05-12] plan-version | /projects 커맨드 갱신 계획
- **Δ vs prior**: `/projects` 커맨드 대상 폴더를 `!Claude / HR-indexData / Smartmeeting - 문서` 기준으로 재정의, 자동 분류 규칙 PLAN v2.2.1 부록 F 기준으로 전면 수정 예정.
- **Raw coords**: `10_RAW/projects/knowledge-management/plans/plan-260512-command-project-renewal.md` (전문)
