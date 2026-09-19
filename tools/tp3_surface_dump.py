#!/usr/bin/env python3
"""Dump the verified golden design-grade TP3 surface as JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tinforge.tp3.surface_decoder import decode_golden_design_grade_surface


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tp3", type=Path)
    parser.add_argument("--base-offset", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    surface = decode_golden_design_grade_surface(
        args.tp3.read_bytes(),
        base_offset=args.base_offset,
    )
    payload = {
        "name": surface.name,
        "origin_x": surface.origin_x,
        "origin_y": surface.origin_y,
        "vertex_count": len(surface.vertices),
        "triangle_count": len(surface.triangles),
        "vertices": [[vertex.x, vertex.y, vertex.z] for vertex in surface.vertices],
        "triangles": [
            {
                "vertices": list(triangle.vertices),
                "neighbors": list(triangle.neighbors),
            }
            for triangle in surface.triangles
        ],
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
