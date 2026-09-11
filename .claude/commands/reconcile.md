---
description: Weekly second-brain reconciliation — detect, resolve, or record conflicting claims without touching raw sources.
---

# /reconcile — Weekly vault reconciliation

`weekly-routine.cmd` invokes this command only after `wiki_lint.py` passes. Read `CLAUDE.md`, `INDEX.md`, and the lint report supplied by the launcher before changing anything.

## 1. Scope and hard stops

- Read `20_WIKI/concepts/`, `20_WIKI/projects/`, `20_WIKI/entities/`, `20_WIKI/decisions/`, project `decisions.md`, and freshness metadata in `10_RAW/`.
- Never modify an existing file under `10_RAW/`.
- Never fabricate a fact, date, person, source, or resolution. If the evidence is insufficient, use `TBD` or create an open conflict.
- Preserve `INDEX.md` and every axis `*-INDEX.md` `<!-- @user:start -->` block byte-for-byte. Regenerate only the `@generated` block when required.
- `synthesis.md`, `LOG.md`, and axis `*-LOG.md` are append-only: every existing byte (table rows AND frontmatter, e.g. `updated`/`last_activity`) must remain unchanged; only add new rows or a new dated section. "Stale" frontmatter in these files is not something this stage fixes — leave it and, if it matters, raise it as a normal wiki-page rewrite candidate for a *different* page, never edit it in place here.
- A rewritten wiki page must retain its prior claim in a new `## History` section with old source/date and new source/date. Entity updates add a `timeline:` row instead of replacing history.
- Use the six-level authority hierarchy in `CLAUDE.md` S-3. A later plan cannot defeat a verified result merely because it is newer.

## 2. Detection — four independent lanes

Run these lanes independently, then combine only their evidence-backed findings:

1. **Claims lane** — compare concepts and project hubs/synthesis for incompatible current claims, dates, numbers, or status.
2. **Entity lane** — compare `20_WIKI/entities/` claims and timelines. Do not create or copy employee IDs, evaluations, salary, health, or other personal data.
3. **Decisions lane** — compare global `20_WIKI/decisions/`, project `decisions.md`, and hub Key Decisions against later verified results.
4. **Source-freshness lane** — compare source dates and wiki dates, using the seven-day freshness window for fast facts and the slower window for durable facts. Freshness alone is not proof of truth.

For each finding record: page, exact section, old claim, competing claim, source links, source dates, authority level, and whether it is a real contradiction or a documented change of mind.

## 3. Evaluation and three-way handling

Evaluate in this order: (1) date, (2) S-3 authority, (3) direct evidence, (4) whether the change is growth rather than error.

- **Clear winner**: rewrite the affected hub/concept/entity/decision page with the verified current claim. Add `## History` (or an entity `timeline:` row), then add one `reconcile` row to the appropriate log.
- **Ambiguous**: create `20_WIKI/decisions/conflict-<kebab>.md` with `type: conflict`, `status: open`, `projects:` array, both claims, both sources, and the exact question requiring a human decision. Leave the existing claim page unchanged. Add one link row to each related project `decisions.md` only when that file exists.
- **Change of mind**: update the current statement while preserving the previous reasoning and date in `## History`; do not label it as an error.

Do not rewrite a page merely because a source is newer. Do not use a conflict note to avoid a clear, verified winner.

## 4. Closing pass and report

After all writes:

1. Regenerate only `INDEX.md`/axis index generated blocks if their page list changed.
2. Append one fixed-schema log row per processed Markdown page. Event must be `reconcile`, never `ingest`.
3. Run `python scripts/wiki_lint.py --format markdown` and stop if it reports a new dead or ambiguous link.
4. Report four lists: automatically resolved (with reason), open conflicts, rewritten pages, and unchanged pages examined. Include raw SHA-256 before/after evidence.

## 5. Result JSON (mandatory)

The weekly gate supplies `run_id`, `week`, the lint JSON path, and an exact result path. Write one JSON object to that path before reporting completion; do not put self-reported hash fields in this JSON because Python owns the snapshots.

```json
{
  "schema_version": 1,
  "run_id": "<gate-run-id>",
  "week": "YYYY-Www",
  "command": "reconcile",
  "completed": true,
  "status": "passed",
  "lint_report": "%TEMP%/claude-weekly-state/lint-YYYY-Www.json",
  "work_items": [{"id": "<lint-finding-or-candidate-id>", "source": "<path>"}],
  "processed": [{"id": "<id>", "path": "<wiki-path>"}],
  "skipped": [{"id": "<id>", "code": "no-evidence", "evidence": "<opening-path-or-lint:id>", "note": "<short reason>"}],
  "out_of_scope": [{"id": "<id>", "reason": "<explicit reason>"}],
  "rewritten": [{"path": "<wiki-path>", "change": "<what changed>"}],
  "conflicts": [{"path": "20_WIKI/decisions/conflict-<kebab>.md"}],
  "drafts": [],
  "log_rows": [{"path": "<log-path>", "event": "reconcile"}],
  "errors": []
}
```

Every lint work item must appear exactly once in `processed`, `skipped`, or `out_of_scope`. A free-form skip explanation without the closed `code` and opening `evidence` is invalid. `completed: true` without the result file is not completion.

## 6. Autonomy

Do not pause to ask the user whether to continue this stage's routine work — just do it and report. Only stop and use `AskUserQuestion` for a critical, irreversible issue (destructive/unrecoverable write, real privacy-boundary exposure, or a genuine authority-hierarchy tie with no evidence-backed winner). Once this result JSON is written, STOP — do not run `/synthesize`, lint auto-fix, or finalize yourself. `weekly_gate.py` owns stage sequencing and runs each stage in its own subprocess with its own snapshot/validate/audit gate; running a later stage yourself breaks that gate (its writes get attributed to the wrong stage's snapshot and fail validation).
