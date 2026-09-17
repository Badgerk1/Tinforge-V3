#!/usr/bin/env python3
"""Create a reproducible non-semantic structural JSON dump of a TP3 file."""
from __future__ import annotations
import argparse
from pathlib import Path
from tinforge.tp3.inspector import inspect_file, to_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tp3", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = to_json(inspect_file(args.tp3))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
