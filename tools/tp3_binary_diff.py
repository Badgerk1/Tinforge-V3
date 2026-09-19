#!/usr/bin/env python3
"""Read-only TP3 binary diff utility with offset-aware structural hints."""
from __future__ import annotations

import argparse
from pathlib import Path

from tinforge.tp3.binary_diff import compare_tp3_files, format_diff_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two TP3 binaries without modifying either file")
    parser.add_argument("old_tp3", type=Path, help="Baseline/original TP3 path")
    parser.add_argument("new_tp3", type=Path, help="Modified/target TP3 path")
    parser.add_argument(
        "--context-bytes",
        type=int,
        default=16,
        help="Bytes of surrounding context to include around each changed range",
    )
    args = parser.parse_args()

    report = compare_tp3_files(args.old_tp3, args.new_tp3, context_bytes=args.context_bytes)
    print(format_diff_report(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
