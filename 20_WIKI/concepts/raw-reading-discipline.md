---
type: concept
date: 2026-05-05
status: draft
tags:
  - raw-reading
  - token-economy
  - discipline
related: [llm-wiki-pattern, mirror-principle]
---

# Raw Reading Discipline

## Definition
10_RAW의 파일을 좌표(item, version/date, section) 없이 통째로 읽는 것을 금지하는 원칙. 좌표가 불명확하면 source-structure 가이드를 먼저 확인하고, 그래도 불명확하면 사용자에게 문의. 이 규칙은 MOS 사건(좌표 없는 full-read로 인한 token 낭비·오류)에서 유래.

## Why It Matters (In This Vault)
Raw 파일(특히 .html/.jsx)은 크고 복잡하다. 좌표 없이 읽으면 token economy를 해치고 무관한 내용이 context를 채운다. LOG 항목마다 raw read 좌표를 기록하게 함으로써 어떤 정보를 어디서 가져왔는지 추적 가능.

## Data Points
| Date | Context (Asset/Project) | Observation |
|---|---|---|
| 2026-05-05 | knowledge-management v2.1.0 | MOS 사건 재발 방지 목적으로 규칙 신설 |
| 2026-05-05 | Phase 3-pilot | plan-document-structure.md 소스 가이드 최초 작성 |

## Related Concepts
- `[[llm-wiki-pattern]]`
- `[[mirror-principle]]`

## Sources
- `[[../../10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.1.0_260505]]` §0 Raw Reading Discipline 행
- `[[sources/plan-document-structure]]`
