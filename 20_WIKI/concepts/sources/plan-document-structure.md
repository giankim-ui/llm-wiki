---
type: source-structure
source_type: plan-document
scope: "10_RAW/projects/knowledge-management/plans/"
date: 2026-05-05
status: stable
maintained_by: claude-code
---

# Source Structure: Plan Document (knowledge-management)

Raw files: `10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_<version>_<date>.md`

## Coordinates Schema

| Dimension | Values / Notes |
|---|---|
| **item** | `PLAN_통합지식관리체계_<version>` |
| **version** | v1.0 (no suffix), v2.0.0, v2.1.0, v2.2.0, v2.2.1 |
| **section** | `§0` changelog, `§1` 이론적 토대, `§2` 폴더 구조, `§3` 워크플로, `§4~§11` 세부 Phase, `§12` 즉시 실행 |

## Key Sections by Purpose

| Section | Content | Lines (approx) |
|---|---|---|
| frontmatter + header | title, date, prev version, 목표 | L1~15 |
| `## 0.` | 버전 변경 요약 (Δ table) | L17~40 |
| `## 1.` | LLM-Wiki 이론 (RAG vs Wiki, 3계층 모델) | L40~100 |
| `## 2.` / `## 3.` | 폴더 구조, Layer 매핑 | L100~200 |
| `Phase X-pilot/full` | 단계별 작업 목록 | L500~620 |

## Reading Discipline

1. 버전 변경 요약만 필요 → `§0` (L17~40) 읽기
2. 폴더 구조 확인 → `§2/§3` 읽기
3. 특정 Phase 작업 확인 → `Phase X` 키워드로 좌표 잡고 해당 구간만 읽기
4. 전체 통독 FORBIDDEN — 항상 좌표 먼저

## Canonical File (현행)

`PLAN_통합지식관리체계_v2.2.1_260505.md` — 가장 최신, 이후 버전이 없으면 이것이 정답
