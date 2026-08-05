#!/usr/bin/env python3
"""
decision-write-guard.py — Claude Code PreToolUse hook (vault-local)

CLAUDE.md 'Writing Scope by Tier' — decision-record 급 결론은
project/asset 축의 단일 decisions.md(또는 20_WIKI/decisions/ 공유 폴더)에
기록해야 한다. 이 훅은 Write/Edit 시점에 그 규칙을 물리 차단한다.

차단 대상: type: decision 또는 type: decision-record 프런트매터를 가진
새 .md 파일이 아래 두 허용 위치 밖에 만들어지는 경우.

허용 위치:
  - 20_WIKI/{projects,assets}/<slug>/decisions.md  (프로젝트/자산 단일 결정 로그)
  - 20_WIKI/decisions/*.md                          (공유 결정·conflict 레코드)

Exit codes:
  0 = 통과
  2 = 차단 (Claude Code 에 stderr 사유 전달)
"""

import json
import os
import re
import sys

if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DECISION_TYPES = frozenset({"decision", "decision-record"})

_TYPE_RE = re.compile(r"^type:\s*[\"']?([a-z0-9\-]+)[\"']?\s*$", re.IGNORECASE | re.MULTILINE)


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def frontmatter_type(content: str) -> str | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    block = content[:end] if end != -1 else content[:2000]
    m = _TYPE_RE.search(block)
    return m.group(1).lower() if m else None


def is_allowed_location(path: str) -> bool:
    path = normalize(path)
    if re.search(r"/20_WIKI/(projects|assets)/[^/]+/decisions\.md$", path):
        return True
    if "/20_WIKI/decisions/" in path:
        return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or not file_path.lower().endswith(".md"):
        sys.exit(0)

    if is_allowed_location(file_path):
        sys.exit(0)

    # 이미 존재하는 파일(과거에 만들어진 detail/history stub 등)의 수정은 막지 않는다.
    # 신규 생성(Write로 새 경로를 만드는 순간)만 차단 대상.
    if os.path.exists(file_path):
        sys.exit(0)

    content = tool_input.get("content") or tool_input.get("new_string") or ""
    if not content:
        sys.exit(0)

    ftype = frontmatter_type(content)
    if ftype in DECISION_TYPES:
        filename = os.path.basename(file_path)
        print(
            f"[decision-write-guard] 차단: `{filename}`에 type: {ftype} 프런트매터.\n"
            f"확정된 decision 내용은 아래 위치에만 기록한다 (CLAUDE.md Writing Scope Tier — 갱신 허용):\n"
            f"  - 20_WIKI/projects/<slug>/decisions.md 또는 20_WIKI/assets/<slug>/decisions.md\n"
            f"    (Decision Log 표에 행 추가 + 상세 내용은 같은 파일 안 하위 섹션에 작성)\n"
            f"  - 20_WIKI/decisions/*.md (여러 프로젝트에 걸친 공유 결정/conflict 레코드일 때만)\n"
            f"새 독립 파일을 만들지 말고 위 파일을 갱신하라. 과거 내용을 대체할 때는 '## History' 섹션으로 보존.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
