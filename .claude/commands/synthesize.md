---
description: Weekly second-brain synthesis — propose at most one evidence-backed concept draft without editing source notes.
---

# /synthesize — Weekly concept synthesis

Run only after `/reconcile` and the lint gate. Read `CLAUDE.md`, `INDEX.md`, the lint report, and the current `concepts-INDEX.md` first.

## 1. Four detection lanes

Search independently for:

1. **Cross-source convergence** — a claim or mechanism supported by at least two independent source notes.
2. **Person/entity convergence** — repeated, non-sensitive entity relationships. Do not create an entity from employee IDs, evaluations, salary, health, or other personal data.
3. **Concept evolution** — a theme updated at least three times with a meaningful change in definition or operating rule.
4. **Orphan rescue candidates** — useful orphan pages from the lint report. Produce a candidate list only; do not edit the orphan page as part of synthesis.

Every candidate must include exact source links, dates, projects, and the reusable abstraction. Anti-fabrication rule: if two sources do not support the same abstraction, report “no candidate.”

## 2. One-draft limit and output

Create **at most one** new draft per ISO week. If a draft already exists for the current week, report candidates without creating another page. A draft is not an accepted concept and requires human approval.

New drafts go to `20_WIKI/concepts/<kebab-title>.md` with:

```yaml
---
type: concept
status: draft
auto_generated: true
date: YYYY-MM-DD
tags:
  - concept
  - synthesis
projects:
  - project-a
  - project-b
---
```

Use the concept page to explain definition, signals, evidence table, prevention/operating rule, and related links. Links leave the concept page; never inject backlinks into source notes. Never copy source paragraphs into the draft.

## 3. Index and report rules

- Add the draft to `concepts-INDEX.md` under `## 자동 후보 (승인 대기)` only. Do not mark it stable.
- Update the project reverse index in `projects-INDEX.md` only when the draft has at least two project links.
- Do not modify `10_RAW/`, source notes, or `synthesis.md` beyond an append-only `synthesize` log row when the draft is actually created.
- Run lint after writing. A new dead/ambiguous link or a missing frontmatter field is a hard stop.
- Report detected candidates, the one draft created (or “none”), source links, projects, and why every other candidate was rejected or deferred.

## 4. Result JSON (mandatory)

The weekly gate supplies `run_id`, `week`, the lint JSON path, and an exact result path. Write one JSON object to that path before reporting completion. Do not put self-reported hash fields in this JSON; Python owns filesystem snapshots.

```json
{
  "schema_version": 1,
  "run_id": "<gate-run-id>",
  "week": "YYYY-Www",
  "command": "synthesize",
  "completed": true,
  "status": "passed",
  "lint_report": "%TEMP%/claude-weekly-state/lint-YYYY-Www.json",
  "work_items": [{"id": "<candidate-id>", "source": "<path>"}],
  "processed": [{"id": "<id>", "path": "20_WIKI/concepts/<kebab>.md"}],
  "skipped": [{"id": "<id>", "code": "weekly-cap", "evidence": "<opening-path-or-lint:id>", "note": "<short reason>"}],
  "out_of_scope": [{"id": "<id>", "reason": "<explicit reason>"}],
  "rewritten": [{"path": "<wiki-path>", "change": "<what changed>"}],
  "conflicts": [],
  "drafts": [{"path": "20_WIKI/concepts/<kebab>.md"}],
  "log_rows": [{"path": "<log-path>", "event": "synthesize"}],
  "errors": []
}
```

The Python gate enforces one draft per week, `auto_generated: true`, `status: draft`, two or more project links, complete work-item accounting, and disclosure of every Wiki write. A missing or malformed result is a failed stage, not a successful “no-op.”
