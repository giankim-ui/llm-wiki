---
name: query
description: LLM-Wiki v2.2 query. Answer from INDEX-first drill-down and recover valuable findings into 20_WIKI/methodology/.
---
<!-- generated-by: public-skill; source: .claude/commands/query.md; source-sha256: 9532b4320bc0f8338c1adc1ad9d4c48a24125432e0ce1984ce2db389edfd5c0f -->

# Query

This is the Codex-compatible public wrapper for the canonical Claude command
`.claude/commands/query.md`. Resolve the nearest project root at runtime (the
nearest ancestor containing `.git`, `.claude`, `CLAUDE.md`, or `AGENTS.md`),
then run the workflow below from that root. The canonical source remains
unchanged.

## 0. Question handling

- Treat the user's current request as the query.
- If no question is supplied, ask one concise question before searching.
- Split multiple questions and process each separately.
- Classify the query scope as `cross-axis`, `asset`, `project`, or `concept/methodology`.

## 1. INDEX entry

Do not grep the whole vault first. Select the entry INDEX from the scope:

| Scope | Entry INDEX |
|---|---|
| `cross-axis` | root `INDEX.md` |
| `asset` | `20_WIKI/assets/assets-INDEX.md` |
| `project` | `20_WIKI/projects/projects-INDEX.md` |
| `concept/methodology` | `20_WIKI/concepts/concepts-INDEX.md` and/or `20_WIKI/methodology/methodology-INDEX.md` |

### Absence check

Do not conclude "not in the vault" merely because INDEX drill-down found no
match. Check these in order before declaring absence:

1. Glob the folder names under `10_RAW/projects/*` and check whether a slug
   matches the query keywords. Do this before searching file contents.
2. If needed, search vault content with an unlimited or sufficiently large
   result limit so older relevant files are not hidden by a default limit.
3. Report "not in the vault" only after both checks fail.

## 2. Drill-down

Identify 2-5 candidate pages from the selected INDEX, then read only those
pages. Do not begin with an exhaustive grep of an asset or topic folder.

### RAW reading discipline

- Determine the coordinate first: item, version/date, section, or item.
- Never read a RAW file end-to-end when a coordinate is sufficient.
- If the coordinate is unclear, consult the relevant structure note under
  `20_WIKI/concepts/sources/`; if it remains unclear, ask the user.
- `10_RAW/` is read-only for this skill. Never modify or create RAW files.

## 3. Answer

Give the answer with sources. Represent every source as an Obsidian wikilink,
including RAW references, for example `[[filename]]`; do not expose filesystem
paths in backticks as source citations.

## 4. File-back decision

| Category | Criterion | Action |
|---|---|---|
| Recoverable finding | A new insight emerges from comparison, analysis, or connections across multiple pages | Create a methodology note |
| Excluded finding | Single-page fact lookup, already covered by an existing note, or no new finding | Do not create a note; still log the query when required |
| Duplicate question | An existing note covers the same topic | Do not create a new note; append a delta to the existing note's `## Answer` or `## Finding` section |

## 5. Create or update the methodology note

When a finding is recoverable, use `_templates/methodology-note.md` and create
`20_WIKI/methodology/<topic-kebab>-<YYMMDD>.md`.

- Keep the topic slug at 24 characters or fewer.
- If the same slug and date already exist, use `-b`, `-c`, and so on.
- Use frontmatter with `type: research`, `scope: methodology`, non-empty
  `tags`, and the question in `question`.
- For a note directly derived from RAW, include
  `mirrors_raw: "[[filename]]"`.
- For a general synthesis, list sources in a `## Pages Read` section instead.

## 6. INDEX and LOG updates

- Add a row for the note under `## All Notes` in
  `20_WIKI/methodology/methodology-INDEX.md`. Do not add a separate methodology
  LOG row.
- Add one root `LOG.md` row per note using:
  `| HH:MM | query | [[note]] | summary <= 60 characters |`.
- Use the note creation time and its creation date for the LOG date section;
  insert same-day rows in ascending time order.
- For `project` scope, add the same event to
  `20_WIKI/projects/projects-LOG.md` under the relevant project slug.
- For `asset` scope, add the same event to `20_WIKI/assets/assets-LOG.md`.
- For `cross-axis` and `concept/methodology` scopes, update only root
  `LOG.md`.
- Before creating a date header, search the entire target LOG for an existing
  header for that date, including suffixed variants. Reuse it and insert only
  the row; do not create duplicate date headers.
- Use the event `query` only. Never use `ingest` for this workflow.

## Binding rules

- Do not leave valuable findings only in chat; recover them to the wiki.
- Never modify or create files under `10_RAW/`.
- Do not use backtick filesystem paths as source citations.
- Do not use inline `tags: []`; provide actual tags for created notes.
