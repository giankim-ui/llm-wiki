import json

lint_path = r"C:\Users\Pulmuone\AppData\Local\Temp\claude-weekly-state\lint-2026-W37.json"
out_path = r"C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\.vault-meta\weekly\reconcile-result-2026-W37.json"

with open(lint_path, encoding="utf-8") as f:
    lint = json.load(f)


def mkid(cat, i):
    return "lint:" + cat + ":" + str(i)


reasons = {
    "allowlisted_dangling_links": "pre-approved allowlisted dangling link (lint config), not a claims/entity/decision/freshness contradiction",
    "duplicate_basenames": "structural filename collision by design (each project owns its own decisions.md/synthesis.md), not a content contradiction - reconcile lanes don't cover file-naming hygiene",
    "empty_sections": "template placeholder scaffolding with no content yet, not a claims conflict between two assertions",
    "missing_frontmatter": "structural frontmatter completeness issue, belongs to lint auto-fix stage not reconcile's contradiction lanes",
    "orphans": "navigation/linking issue (unlinked page), not a claims/entity/decision/freshness contradiction",
    "raw_reference_notes": "target is inside 10_RAW (read-only raw) or points outside the vault; reconcile must never modify 10_RAW and this is a link-hygiene note, not a semantic contradiction",
}

work_items = []
out_of_scope = []

for cat, reason in reasons.items():
    items = lint.get(cat, [])
    for i, item in enumerate(items):
        src = item.get("source") or (item.get("paths") or ["?"])[0]
        wid = mkid(cat, i)
        work_items.append({"id": wid, "source": src})
        out_of_scope.append({"id": wid, "reason": reason + " (source: " + str(src) + ")"})

result = {
    "schema_version": 1,
    "run_id": "7ebaea23cbca4482883f2bd44b08b0fd",
    "week": "2026-W37",
    "command": "reconcile",
    "completed": True,
    "status": "passed",
    "lint_report": lint_path,
    "work_items": work_items,
    "processed": [],
    "skipped": [
        {
            "id": "manual:mailing-agent-research-drift",
            "code": "authority-tie",
            "evidence": "20_WIKI/decisions/conflict-mailing-research-content-drift.md",
            "note": "pre-existing open conflict re-reviewed under claims/source-freshness lanes; no new evidence this week (same ctime, drifted content, user decision still pending) - left unchanged, not re-litigated"
        }
    ],
    "out_of_scope": out_of_scope,
    "rewritten": [],
    "conflicts": [],
    "drafts": [],
    "log_rows": [],
    "errors": []
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("work_items:", len(result["work_items"]))
print("out_of_scope:", len(result["out_of_scope"]))
print("skipped:", len(result["skipped"]))
