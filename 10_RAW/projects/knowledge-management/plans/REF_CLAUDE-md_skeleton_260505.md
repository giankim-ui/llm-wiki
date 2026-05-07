---
name: 루트 CLAUDE.md 골격 (Phase 1 작성 대상)
description: KM v2.2.x Phase 1에서 vault 루트에 작성될 CLAUDE.md baseline 골격
type: reference
date: 2026-05-05
related_plan: PLAN_통합지식관리체계_v2.2.1_260505.md
status: stable
---

# 루트 CLAUDE.md 골격 (Phase 1 작성 대상, v2.2.x 정본)

> 본 문서는 KM v2.2.x Phase 1 에서 볼트 루트에 작성할 `CLAUDE.md` 의 baseline 골격이다.
> Plan 본문(`PLAN_통합지식관리체계_v2.2.1_*.md`)에서 분리해 별도 산출물로 관리한다.
> Phase 1 시작 시 본 골격을 그대로 볼트 루트 `CLAUDE.md` 로 복사한 뒤 운영 경험을 반영해 미세조정한다.

---

```markdown
# Vault CLAUDE.md (LLM-Wiki Schema v2.2)

This vault is an LLM-maintained dual-axis knowledge base. You are the maintainer.

## Folder ↔ Layer Mapping (BINDING)
- `10_*`, `90_*`, `_attachments/`, `S-anlyz*/`  → Layer 1 (Raw). NEVER modify.
- `20_*`, root `INDEX.md`/`LOG.md`/`MAP.md`  → Layer 2 (Wiki). LLM writes only. .md only.
- `/CLAUDE.md`, `_templates/`  → Layer 3 (Schema).

## Two Axes
- **Asset axis**: `10_RAW/assets/<COUNTRY>-<TICKER>/`, `20_WIKI/assets/<TICKER>/`
- **Project axis**: `10_RAW/projects/<slug>/`, `20_WIKI/projects/<slug>/`
- Shared: `20_WIKI/{concepts,themes,comparisons,industry,macro,frameworks,methodology,screening}/`

## 3-Tier Navigation
- Tier 1: `/INDEX.md` dashboard, `/LOG.md` cross-axis recent
- Tier 2: `20_WIKI/{projects,assets}/INDEX.md` + `LOG.md`
- Tier 3: `20_WIKI/{projects,assets}/<item>/INDEX.md`

## Rules
1. NEVER modify Layer 1 raw.
2. NEVER modify `S-anlyz*/CLAUDE.md` or `S-anlyz*/.claude/`.
3. ALWAYS read root `INDEX.md` for navigation queries; axis INDEX for axis-scoped queries.
4. ALWAYS append to LOG.md (axis-appropriate) after ingest/query/lint with `## [YYYY-MM-DD HH:MM] <event> | <subject>`.
5. ALWAYS ensure frontmatter on every .md.
6. NEVER skip cross-reference: ingest must touch INDEX.md(s) + LOG.md + ≥1 entity/concept/theme/comparison page besides item folder.
7. NEVER duplicate analysis/document content in wiki. synthesis.md = compounding log only (5~10 lines per item, Δ vs prior).

## Raw Reading Discipline (MOS Lesson — BINDING)
1. NEVER Read .json/.html/.md in `10_RAW/` in full. Coordinates first.
2. Coordinates = (item, version/date, section/Item).
3. If unknown, consult `20_WIKI/concepts/sources/...-structure.md`.
4. If still unclear, ASK user. Free-exploration full-read FORBIDDEN.
5. Each ingest's LOG entry must record raw read coordinates or "none".

## Mirror Principle
1. Information for Obsidian graph/search/Dataview must exist as .md in `20_WIKI/`.
2. Raw .jsx/.html/.json/.md stays in `10_RAW/`.
3. Wiki .md derived from raw must include `mirrors_raw: "[[10_RAW/...]]"` frontmatter.

## Status Vocabulary (BINDING)
- Project: `active | blocked | paused | done | archived`
- Asset: `watchlist | holding | archived`
- Concept/Theme/Comparison/Framework: `draft | stable`
- Plan (raw): `active | done`
- `status` change requires user confirm; LLM proposes only.

## LOG Event Vocabulary (BINDING)
decision, plan-version, result, phase-start, phase-complete, status-change, concept-extracted, theme-extracted, handoff, ingest, query, lint

## Workflows
- Reading Discipline: see PLAN v2.2.x §6.0
- Ingest: §6.1
- Query: §6.2
- Lint: §6.3

## Frontmatter type Vocabulary
asset-index, asset-synthesis, project-index, project-synthesis, concept, theme, comparison, framework, plan, research, chat-extract, source-structure, handoff, log, index
```

---

## 운영 메모

- 본 골격은 Phase 1 작업 직전에 Phase 0~v2.2 plan 운영 경험에 따라 미세 수정 가능
- Phase 5 운영 안착 시점에 본 골격이 실제 운영 룰을 정확히 반영하는지 재검증
- 골격 변경 시: 본 파일 갱신 + plan v2.2.x patch 또는 v2.3 발행
