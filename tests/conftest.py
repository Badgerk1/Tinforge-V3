import os
from pathlib import Path

import pytest

from tinforge.surface import SurfaceTIN, SurfaceVertex, build_triangle_adjacency

GOLDEN_TP3_ENV = "TINFORGE_GOLDEN_TP3_PATH"


@pytest.fixture
def tiny_surface() -> SurfaceTIN:
    vertices = (
        SurfaceVertex(x=0.0, y=0.0, z=100.0),
        SurfaceVertex(x=10.0, y=0.0, z=101.0),
        SurfaceVertex(x=10.0, y=10.0, z=102.0),
        SurfaceVertex(x=0.0, y=10.0, z=103.0),
    )
    triangles = build_triangle_adjacency(
        len(vertices),
        (
            (0, 1, 2),
            (0, 2, 3),
        ),
    )
    return SurfaceTIN(
        name="tiny synthetic surface",
        origin_x=295399.97869873,
        origin_y=4843987.442024235,
        vertices=vertices,
        triangles=triangles,
    )


@pytest.fixture(scope="session")
def original_professional_tp3_bytes() -> bytes:
    configured_path = os.environ.get(GOLDEN_TP3_ENV, "").strip()
    candidate_paths = [
        Path(configured_path) if configured_path else None,
        Path("/tmp/Purolator_NP_2026.tp3"),
        Path("/tmp/inputs/Purolator NP 2026.tp3"),
        Path("/tmp/inputs/Purolator_NP_2026.tp3"),
    ]
    for path in candidate_paths:
        if path is not None and path.is_file():
            return path.read_bytes()
    pytest.skip(
        "Original professional TP3 fixture not found. "
        f"Set {GOLDEN_TP3_ENV} to the authentic 'Purolator NP 2026.tp3' path."
    )
