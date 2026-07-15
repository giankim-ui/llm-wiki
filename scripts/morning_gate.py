#!/usr/bin/env python3
"""Launcher gate: exec claude with morning instruction once per day.

Usage: python scripts/morning_gate.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent
MARKER_PATH = VAULT_ROOT / "scripts" / ".morning_last_run"

INSTRUCTION = (
    "[MORNING AUTORUN] 지금 즉시 /projects 스킬을 실행해 archive 이관을 끝내고, "
    "완료되면 이어서 /ingest 스킬을 실행하라. 다른 안내 없이 바로 /projects부터 시작."
)


def main() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    last_run = MARKER_PATH.read_text(encoding="utf-8").strip() if MARKER_PATH.exists() else ""

    if last_run == today:
        args = ["cmd", "/c", "claude"]
    else:
        args = ["cmd", "/c", "claude", INSTRUCTION]

    rc = subprocess.call(args, cwd=str(VAULT_ROOT))

    if last_run != today:
        MARKER_PATH.write_text(today, encoding="utf-8")

    return rc


if __name__ == "__main__":
    sys.exit(main())
