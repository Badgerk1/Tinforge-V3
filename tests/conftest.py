import pytest

from tinforge.surface import SurfaceTIN, SurfaceVertex, build_triangle_adjacency


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
