---
type: concept
date: 2026-05-05
status: draft
tags:
  - mirror-principle
  - obsidian
  - wiki-structure
related: [llm-wiki-pattern, raw-reading-discipline]
---

# Mirror Principle

## Definition
Obsidian graph/search/Dataview가 인식할 정보는 반드시 `20_WIKI/`에 .md로 존재해야 한다. 원본 .jsx/.html/.json은 `10_RAW/`에 보존하고, LLM이 핵심 정보를 `20_WIKI/` .md로 미러링한다. 미러 .md는 `mirrors_raw:` frontmatter로 원본과 1:1 연결.

## Why It Matters (In This Vault)
Obsidian은 .md만 인덱싱한다. 분析 대시보드(.jsx/.html)의 인사이트가 wiki에 .md로 미러되지 않으면 Dataview/그래프에서 보이지 않는다. mirrors_raw 필드가 원본-미러 무결성 검증의 기준.

## Data Points
| Date | Context (Asset/Project) | Observation |
|---|---|---|
| 2026-05-05 | knowledge-management v2.1.0 | .md 미러링 원칙 최초 명문화 |
| 2026-05-05 | US-MSFT INDEX.md | mirrors_raw: "[[10_RAW/assets/US-MSFT/]]" 첫 적용 |

## Related Concepts
- `[[llm-wiki-pattern]]`
- `[[raw-reading-discipline]]`

## Sources
- `[[../../10_RAW/projects/knowledge-management/plans/PLAN_통합지식관리체계_v2.1.0_260505]]` §0 Mirror Principle 행
