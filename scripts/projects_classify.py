"""
Classify .md files in vault archive folders into project slugs and types.
Outputs JSON with classification results and summary.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# Classification rules: (pattern, slug, type)
# Ordered by priority — first match wins
RULES = [
    # knowledge-management / plans
    ("PLAN_통합지식관리", "knowledge-management", "plans"),
    ("PLAN_km-", "knowledge-management", "plans"),
    ("PLAN_raw-data-preservation", "knowledge-management", "plans"),
    ("PLAN_phase-model", "knowledge-management", "plans"),
    ("PLAN-phase-model", "knowledge-management", "plans"),
    ("REF_CLAUDE-md_skeleton", "knowledge-management", "plans"),
    ("lim-wiki", "knowledge-management", "plans"),

    # screening-mode / plans (before multi-agent to avoid PLAN_ prefix collision)
    ("PLAN_jp-sync-screening", "screening-mode", "plans"),
    ("PLAN_edinet-api-integration", "screening-mode", "plans"),

    # multi-agent-stock-analysis / plans (PLAN_ prefix patterns)
    ("PLAN_cross-country-pipeline-sync", "multi-agent-stock-analysis", "plans"),
    ("PLAN_pipeline-sync-agent", "multi-agent-stock-analysis", "plans"),
    ("PLAN_investing-scraper", "multi-agent-stock-analysis", "plans"),
    ("PLAN_sec-scraper", "multi-agent-stock-analysis", "plans"),
    ("PLAN_us-sync-screening-cyclical", "multi-agent-stock-analysis", "plans"),
    ("PLAN_data-collector", "multi-agent-stock-analysis", "plans"),
    ("PLAN_S-anlyz-jp", "multi-agent-stock-analysis", "plans"),

    # multi-agent-stock-analysis / clippings (S-anlyz specific)
    ("CLAUDE_KR", "multi-agent-stock-analysis", "clippings"),
    ("jp-stock-analysis-framework", "multi-agent-stock-analysis", "clippings"),
    ("jSX-HTML-변환규칙", "multi-agent-stock-analysis", "clippings"),
    ("investing-scriper", "multi-agent-stock-analysis", "clippings"),
    ("supervisor-v1", "multi-agent-stock-analysis", "clippings"),
]

# Result patterns that inherit slug from PLAN mapping
RESULT_PREFIXES = ("RESULT_", "result-", "result-2026")
RESULT_EXACT = ("result.md",)

# HANDOFF patterns
HANDOFF_PREFIX = "HANDOFF"

# Research patterns
RESEARCH_PREFIX = "research"


def _is_sanlyz_folder(src_path: Path) -> bool:
    """Return True if the file is under an S-anlyz* subfolder."""
    parts = src_path.parts
    return any(p.lower().startswith("s-anlyz") for p in parts)


def _get_src_folder_tag(src_path: Path) -> str:
    """Return which of the 4 source folders this file came from."""
    parts = src_path.parts
    for p in parts:
        if p.lower().startswith("s-anlyz"):
            return p
    return "archive"


def classify_file(src_path: Path) -> dict:
    name = src_path.name
    name_lower = name.lower()
    is_sanlyz = _is_sanlyz_folder(src_path)
    ctime = os.stat(src_path).st_ctime

    import datetime
    ctime_iso = datetime.datetime.fromtimestamp(ctime).astimezone().isoformat(timespec="seconds")

    slug, file_type, confidence, reason = None, None, None, None

    # --- HANDOFF ---
    if name_lower.startswith(HANDOFF_PREFIX.lower()):
        slug = "multi-agent-stock-analysis" if is_sanlyz else "knowledge-management"
        file_type = "handoffs"
        confidence = "L1"
        reason = f"HANDOFF prefix; source={'S-anlyz*' if is_sanlyz else 'cwd'}/archive"
        return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- research clippings ---
    if name_lower.startswith(RESEARCH_PREFIX):
        slug = "multi-agent-stock-analysis" if is_sanlyz else "knowledge-management"
        file_type = "clippings"
        confidence = "L1"
        reason = f"research* prefix; source={'S-anlyz*' if is_sanlyz else 'cwd'}/archive"
        return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- result.md exact or result-2026* ---
    if name_lower == "result.md" or name_lower.startswith("result-2026"):
        if is_sanlyz:
            slug = "multi-agent-stock-analysis"
            file_type = "clippings"
            confidence = "L1"
            reason = "result.md/result-2026* in S-anlyz*/archive → clippings"
        else:
            slug = "knowledge-management"
            file_type = "results"
            confidence = "L2"
            reason = "result.md/result-2026* in cwd/archive → results (prefix rule)"
        return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- RESULT_ / result- prefix (results type) ---
    if name.startswith("RESULT_") or name_lower.startswith("result-"):
        # Apply same PLAN slug mapping via rules
        matched_slug = _match_plan_slug(name)
        if matched_slug:
            slug = matched_slug
            file_type = "results"
            confidence = "L1"
            reason = f"RESULT/result- prefix with plan slug match: {matched_slug}"
        else:
            # Folder-based fallback
            if is_sanlyz:
                slug = "multi-agent-stock-analysis"
            else:
                slug = "knowledge-management"
            file_type = "results"
            confidence = "L2"
            reason = f"result- prefix; folder fallback slug={'multi-agent-stock-analysis' if is_sanlyz else 'knowledge-management'}"
        return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- S-anlyz specific clipping patterns ---
    if is_sanlyz:
        for pattern in ("CLAUDE_KR", "jp-stock-analysis-framework", "jSX-HTML-변환규칙",
                        "investing-scriper", "supervisor-v1"):
            if name_lower.startswith(pattern.lower()):
                slug = "multi-agent-stock-analysis"
                file_type = "clippings"
                confidence = "L1"
                reason = f"S-anlyz clipping pattern: {pattern}*"
                return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- PLAN rules (L1: explicit named patterns) ---
    for pattern, p_slug, p_type in RULES:
        if name_lower.startswith(pattern.lower()):
            slug = p_slug
            file_type = p_type
            confidence = "L1"
            reason = f"Matched rule pattern: {pattern}*"
            return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- plan*.md / plan-*.md (L2: prefix rule, folder-aware) ---
    if name_lower.startswith("plan") and name_lower.endswith(".md"):
        if is_sanlyz:
            slug = "multi-agent-stock-analysis"
        else:
            slug = "knowledge-management"
        file_type = "plans"
        confidence = "L2"
        reason = f"plan*.md prefix; folder={'S-anlyz*' if is_sanlyz else 'cwd'}/archive"
        return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- plan-jp-*, plan-sonnet*, plan-industry* in S-anlyz ---
    if is_sanlyz:
        for sub in ("plan-jp-", "plan-sonnet", "plan-industry"):
            if name_lower.startswith(sub):
                slug = "multi-agent-stock-analysis"
                file_type = "plans"
                confidence = "L2"
                reason = f"S-anlyz plan sub-pattern: {sub}*"
                return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)

    # --- No match → L3 unknown ---
    slug = "unknown"
    file_type = "unknown"
    confidence = "L3"
    reason = "No classification rule matched; needs content analysis"
    return _make_result(src_path, ctime_iso, slug, file_type, confidence, reason)


def _match_plan_slug(name: str) -> str | None:
    """Return slug based on PLAN naming rules applied to a result filename."""
    name_lower = name.lower()
    km_patterns = [
        "통합지식관리", "km-", "raw-data-preservation", "phase-model",
        "claude-md_skeleton", "lim-wiki",
    ]
    for p in km_patterns:
        if p.lower() in name_lower:
            return "knowledge-management"
    screening_patterns = ["jp-sync-screening", "edinet-api-integration"]
    for p in screening_patterns:
        if p.lower() in name_lower:
            return "screening-mode"
    multi_patterns = [
        "cross-country-pipeline-sync", "pipeline-sync-agent", "investing-scraper",
        "sec-scraper", "us-sync-screening-cyclical", "data-collector", "s-anlyz-jp",
    ]
    for p in multi_patterns:
        if p.lower() in name_lower:
            return "multi-agent-stock-analysis"
    return None


def _make_result(src_path: Path, ctime_iso: str, slug: str, file_type: str,
                 confidence: str, reason: str) -> dict:
    return {
        "src_path": str(src_path),
        "ctime_iso": ctime_iso,
        "slug": slug,
        "type": file_type,
        "confidence": confidence,
        "reason": reason,
    }


def scan_folder(folder: Path) -> list[dict]:
    results = []
    if not folder.exists():
        return results
    for path in folder.rglob("*.md"):
        if path.is_file():
            try:
                results.append(classify_file(path))
            except Exception as e:
                results.append({
                    "src_path": str(path),
                    "ctime_iso": None,
                    "slug": "error",
                    "type": "error",
                    "confidence": "L3",
                    "reason": f"Exception during classification: {e}",
                })
    return results


def main():
    parser = argparse.ArgumentParser(description="Classify vault archive .md files into project slugs.")
    parser.add_argument("--vault-root", type=str, default=None,
                        help="Vault root directory (default: parent of script location)")
    parser.add_argument("--output-file", type=str, default=None,
                        help="Write JSON output to file instead of stdout")
    args = parser.parse_args()

    if args.vault_root:
        vault_root = Path(args.vault_root)
    else:
        vault_root = Path(__file__).parent.parent

    source_folders = [
        vault_root / "archive",
        vault_root / "S-anlyz" / "archive",
        vault_root / "S-anlyz-kr" / "archive",
        vault_root / "S-anlyz-jp" / "archive",
    ]

    all_files: list[dict] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scan_folder, folder): folder for folder in source_folders}
        for future in as_completed(futures):
            all_files.extend(future.result())

    # Sort by src_path for deterministic output
    all_files.sort(key=lambda x: x["src_path"])

    summary = {
        "total": len(all_files),
        "km": sum(1 for f in all_files if f["slug"] == "knowledge-management"),
        "multi": sum(1 for f in all_files if f["slug"] == "multi-agent-stock-analysis"),
        "screening": sum(1 for f in all_files if f["slug"] == "screening-mode"),
        "unknown": sum(1 for f in all_files if f["slug"] in ("unknown", "error")),
    }

    output = {"files": all_files, "summary": summary}
    json_str = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output_file:
        Path(args.output_file).write_text(json_str, encoding="utf-8")
        print(f"Output written to {args.output_file}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
