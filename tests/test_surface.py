import pytest

from tinforge.surface import (
    NonManifoldTINError,
    SurfaceTIN,
    SurfaceTriangle,
    SurfaceVertex,
    build_triangle_adjacency,
    validate_tin,
    xy_area_tolerance,
)


def test_build_triangle_adjacency_is_deterministic(tiny_surface: SurfaceTIN):
    triangles = build_triangle_adjacency(
        len(tiny_surface.vertices),
        (
            (0, 1, 2),
            (0, 2, 3),
        ),
    )
    assert triangles == tiny_surface.triangles
    assert triangles[0].neighbors == (-1, -1, 1)
    assert triangles[1].neighbors == (0, -1, -1)


def test_validate_tin_accepts_tiny_surface_fixture(tiny_surface: SurfaceTIN):
    validate_tin(tiny_surface)


def test_validate_tin_rejects_missing_neighbor(tiny_surface: SurfaceTIN):
    broken = SurfaceTIN(
        name=tiny_surface.name,
        origin_x=tiny_surface.origin_x,
        origin_y=tiny_surface.origin_y,
        vertices=tiny_surface.vertices,
        triangles=(
            SurfaceTriangle(vertices=(0, 1, 2), neighbors=(-1, -1, -1)),
            tiny_surface.triangles[1],
        ),
    )
    with pytest.raises(ValueError, match="missing reciprocal neighbor"):
        validate_tin(broken)


def test_validate_tin_rejects_wrong_neighbor(tiny_surface: SurfaceTIN):
    vertices = tiny_surface.vertices + (
        SurfaceVertex(x=20.0, y=0.0, z=104.0),
    )
    triangles = build_triangle_adjacency(
        len(vertices),
        (
            (0, 1, 2),
            (0, 2, 3),
            (1, 4, 2),
        ),
    )
    broken = SurfaceTIN(
        name="wrong neighbor",
        origin_x=tiny_surface.origin_x,
        origin_y=tiny_surface.origin_y,
        vertices=vertices,
        triangles=(
            SurfaceTriangle(vertices=triangles[0].vertices, neighbors=(-1, 2, 2)),
            triangles[1],
            triangles[2],
        ),
    )
    with pytest.raises(ValueError, match="incorrect neighbor references"):
        validate_tin(broken)


def test_validate_tin_rejects_non_reciprocal_neighbor(tiny_surface: SurfaceTIN):
    broken = SurfaceTIN(
        name=tiny_surface.name,
        origin_x=tiny_surface.origin_x,
        origin_y=tiny_surface.origin_y,
        vertices=tiny_surface.vertices,
        triangles=(
            tiny_surface.triangles[0],
            SurfaceTriangle(vertices=(0, 2, 3), neighbors=(1, -1, -1)),
        ),
    )
    with pytest.raises(ValueError, match="non-reciprocal"):
        validate_tin(broken)


def test_validate_tin_rejects_incorrect_edge_neighbor(tiny_surface: SurfaceTIN):
    broken = SurfaceTIN(
        name=tiny_surface.name,
        origin_x=tiny_surface.origin_x,
        origin_y=tiny_surface.origin_y,
        vertices=tiny_surface.vertices,
        triangles=(
            tiny_surface.triangles[0],
            SurfaceTriangle(vertices=(0, 2, 3), neighbors=(0, 0, -1)),
        ),
    )
    with pytest.raises(ValueError, match="boundary edge"):
        validate_tin(broken)


def test_validate_tin_rejects_degenerate_triangle():
    surface = SurfaceTIN(
        name="degenerate",
        origin_x=0.0,
        origin_y=0.0,
        vertices=(
            SurfaceVertex(x=0.0, y=0.0, z=0.0),
            SurfaceVertex(x=1.0, y=0.0, z=0.0),
        ),
        triangles=(SurfaceTriangle(vertices=(0, 1, 1)),),
    )
    with pytest.raises(ValueError, match="reuses a vertex index"):
        validate_tin(surface)


def test_validate_tin_rejects_near_degenerate_triangle():
    vertices = (
        SurfaceVertex(x=0.0, y=0.0, z=0.0),
        SurfaceVertex(x=1.0, y=0.0, z=0.0),
        SurfaceVertex(x=1.0, y=1e-13, z=0.0),
    )
    surface = SurfaceTIN(
        name="near degenerate",
        origin_x=0.0,
        origin_y=0.0,
        vertices=vertices,
        triangles=(SurfaceTriangle(vertices=(0, 1, 2)),),
    )
    assert xy_area_tolerance(vertices) == pytest.approx(1e-12)
    with pytest.raises(ValueError, match="near-degenerate"):
        validate_tin(surface)


def test_validate_tin_rejects_invalid_indexes(tiny_surface: SurfaceTIN):
    broken = SurfaceTIN(
        name=tiny_surface.name,
        origin_x=tiny_surface.origin_x,
        origin_y=tiny_surface.origin_y,
        vertices=tiny_surface.vertices,
        triangles=(SurfaceTriangle(vertices=(0, 1, 99)),),
    )
    with pytest.raises(ValueError, match="invalid vertex 99"):
        validate_tin(broken)


def test_validate_tin_rejects_non_manifold_geometry():
    surface = SurfaceTIN(
        name="non manifold",
        origin_x=0.0,
        origin_y=0.0,
        vertices=(
            SurfaceVertex(x=0.0, y=0.0, z=0.0),
            SurfaceVertex(x=1.0, y=0.0, z=0.0),
            SurfaceVertex(x=0.0, y=1.0, z=0.0),
            SurfaceVertex(x=0.0, y=-1.0, z=0.0),
            SurfaceVertex(x=1.0, y=1.0, z=0.0),
        ),
        triangles=(
            SurfaceTriangle(vertices=(0, 1, 2)),
            SurfaceTriangle(vertices=(1, 0, 3)),
            SurfaceTriangle(vertices=(0, 1, 4)),
        ),
    )
    with pytest.raises(NonManifoldTINError, match="shared by more than two triangles"):
        validate_tin(surface)


def test_build_triangle_adjacency_rejects_non_manifold_edges():
    with pytest.raises(NonManifoldTINError, match="shared by more than two triangles"):
        build_triangle_adjacency(
            5,
            (
                (0, 1, 2),
                (1, 0, 3),
                (0, 1, 4),
            ),
        )
